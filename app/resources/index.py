import logging
from typing import Dict, List
from fastapi import APIRouter
from fastapi_cache.decorator import cache
from fastapi import status
from utility.utils import (
    ingest_single_document, 
    bulk_ingest_documents
)
from utility.model import DataIngestionSchema

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/index", status_code=status.HTTP_201_CREATED)
async def index_single_document(document: DataIngestionSchema):
    return ingest_single_document(document)

@router.post("/bulk_index", status_code=status.HTTP_201_CREATED)
async def index_bulk_documents(documents: List[DataIngestionSchema]):
    return bulk_ingest_documents(documents)
