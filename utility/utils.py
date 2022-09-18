from asyncio.log import logger
import os
from typing import Dict, List
from utility.es_utils import es
from elasticsearch import helpers
from fastapi import HTTPException, status
import traceback
from datetime import datetime, date
from utility.model import (
    DataIngestionSchema,
    DocumentType,
    ExchangeStructure,
    Permission,
    SearchQuerySchema
)
from utility.lens.queries import (
    get_followers_query,
    get_profiles_query
)
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import json


lens_mainnet_environment = os.getenv("LENS_DEV_ENV_CHAIN", "https://api.lens.dev/")
transport = RequestsHTTPTransport(
    url=lens_mainnet_environment,
    use_json=True
)
client = Client(transport=transport, fetch_schema_from_transport=True)
index_name = os.getenv("ENCRYPTED_INDEX_NAME", "encrypted_index_ethberlin")
exchange_index = os.getenv("EXCHANGE_INDEX_NAME", "exchange_index")

def raise_custom_exception(status_code=\
    status.HTTP_400_BAD_REQUEST, message=""):
    raise HTTPException(
        status_code=status_code,
        detail=message
    )


def enrich_data(document: DataIngestionSchema):
    doc_schema = {}
    if not document.text:
        raise_custom_exception(
            message=f"The text can not be empty {document}"
        )
    doc_schema['text'] = document.text
    if not document.text:
        raise_custom_exception(
            message=f"Please specify if the document is shared {document}"
        )
    doc_schema['shared'] = document.shared
    if not document.creator_address:
        raise_custom_exception(
            message=f"Please specify the creator address {document}"
        )
    doc_schema['created_address'] = document.creator_address
    doc_schema['shared_addresses'] = document.shared_addresses
    doc_schema['document_type'] = document.document_type
    doc_schema['created'] = datetime.now()
    return doc_schema


def ingest_single_document(document: DataIngestionSchema):
    try:
        es.index(index=index_name, body=enrich_data(document))
        return {"message":"document indexed successfully"}
    except HTTPException as err:
        err = traceback.format_exc()
        logger.error(f"HttpException: Error while indexing, {err}")
        raise err
    except Exception:
        err = traceback.format_exc()
        logger.error(f"Error while indexing single document, {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while performing indexing request for single documents"
        )


def bulk_ingest_documents(documents: List[DataIngestionSchema]):
    try:
        actions = []
        for ix in range(len(documents)):
            doc_schema = {}
            document = documents[ix]
            doc_schema["_index"] = index_name
            doc_schema["_source"] = enrich_data(document)
            actions.append(doc_schema)
        helpers.bulk(es, actions)
        return {"message": f"Indexed {len(documents)} successfully!"}
    except HTTPException as err:
        err = traceback.format_exc()
        logger.error(f"HttpException: Error while bulk indexing, {err}")
        raise err
    except Exception:
        err = traceback.format_exc()
        logger.error(f"Error while bulk indexing, {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while performing bulk indexing request"
        )

def get_text_query(text):
    if not text:
        return 
    return {"match_phrase": {"text": text}}
    

def search(search_parameters: SearchQuerySchema):
    sort_by = {
        "created": search_parameters.date_sort
    }
    page = search_parameters.page
    query = {
        "query": {
            "bool": {
                "must_not": [],
                "must": [],
                "should": [],
            }
        }, 
        "size": search_parameters.size,
        "from": (page - 1 if page > 0 else 0) * search_parameters.size,
        "sort": sort_by
    }
    if search_parameters.creator_address:
        q = {
            "match_phrase": {
                "creator_address": search_parameters.creator_address
            }
        }
        query["query"]["bool"]["must"].append(q)
    text_query = get_text_query(search_parameters.text)
    if text_query:
        query["query"]["bool"]["must"].append(text_query)
    if not search_parameters.document_type == DocumentType.all:
        query["query"]["bool"]["must"].append(
            {
                "match": {
                    "document_type": search_parameters.document_type
                }
            }
        )
    if not search_parameters.shared == Permission.all:
        if search_parameters.shared == Permission.private:
            shared_q = {
                "match": {
                    "shared": False
                }
            }
        elif search_parameters.shared == Permission.shared:
            shared_q = {
                "match": {
                    "shared": True
                }
            }
        query["query"]["bool"]["must"].append(
            shared_q
        )
    created_at_q = {}
    if search_parameters.from_date:
        created_at_q['gte'] = search_parameters.from_date
    if search_parameters.to_date and search_parameters.to_date!=date.today():
        created_at_q['lte'] = search_parameters.to_date
    res = es.search(index=index_name, body=query)
    return {
        "query": search_parameters,
        "total_count": res["hits"]["total"]["value"],
        "data":  res["hits"]["hits"]
    }


def extract_user_info_from_lens(wallet_address: str):
    try:
        query = gql(get_profiles_query([wallet_address]))
        response = client.execute(query)
        result = response.get("profiles", []).get("items", [])
        if result and isinstance(result, list):
            return result[0]
        return {}
    except Exception as err:
        logger.error(err)
        raise HTTPException(
            detail=f"Could not find lens profile information for {wallet_address}, error: {err}",
            status_code=status.HTTP_400_BAD_REQUEST
        )

def fetch_followers(user_id, offset=0):
    query = gql(get_followers_query(user_id, offset))
    response = client.execute(query)
    page_info = response.get('followers', {}).get('pageInfo', {})
    offset = json.loads(page_info.get('next', {})).get('offset')
    total_count = page_info.get('totalCount')
    return response.get('followers', {}).get('items', []), total_count, offset


def fetch_follower_list(user_lens_id: str):
    try:
        followers = []
        follower_list, _, offset = fetch_followers(user_lens_id)
        followers.extend(follower_list)
        while follower_list:
            follower_list, _, offset = fetch_followers(user_lens_id, offset)
            followers.extend(follower_list)
        return followers
    except Exception as err:
        logger.error(err)
        raise HTTPException(
            detail=f"Could not find followers list for the user '{user_lens_id}', error: {err}",
            status_code=status.HTTP_400_BAD_REQUEST
        )

def save_exchange_data(exchange: ExchangeStructure):
    try:
        data = {
            "public_key": exchange.public_key,
            "aes_key": exchange.aes_key
        }
        es.index(
            index=exchange_index, body=data
        )
        return {
            "message": "Exchange saved successfully!"
        }
    except Exception as err:
        logger.error(err)
        raise HTTPException(
            detail=f"Could not save the exchange {err}",
            status_code=status.HTTP_400_BAD_REQUEST
        )

def get_exchange_data(key: str):
    try:
        query = {
            "query": {
                "match_phrase": {
                    "public_key": key
                }
            }
        }
        res = es.search(index=exchange_index, body=query)
        return {
            "exchange_data": res["hits"]["hits"]
        }
    except Exception as err:
        logger.error(err)
        raise HTTPException(
            detail=f"Could not get the exchange {err}",
            status_code=status.HTTP_400_BAD_REQUEST
        )