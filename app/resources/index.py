import logging
from typing import Dict, List
from fastapi import APIRouter
from fastapi_cache.decorator import cache
from fastapi import status, Body
from utility.utils import (
    ingest_single_document, 
    bulk_ingest_documents,
    save_exchange_data,
    get_exchange_data
)
from utility.model import DataIngestionSchema, ExchangeStructure

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/index", status_code=status.HTTP_201_CREATED)
async def index_single_document(document: DataIngestionSchema):
    return ingest_single_document(document)

@router.post("/bulk_index", status_code=status.HTTP_201_CREATED)
async def index_bulk_documents(documents: List[DataIngestionSchema]):
    return bulk_ingest_documents(documents)

@router.post("/persist_exchange", status_code=status.HTTP_201_CREATED)
async def persist_exchange(exchange: ExchangeStructure):
    return save_exchange_data(exchange)

@router.post("/get_exchange", status_code=status.HTTP_200_OK)
async def get_exchange(public_key: str=Body(...,embed=True)):
    return get_exchange_data(public_key)
