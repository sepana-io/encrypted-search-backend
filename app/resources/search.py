import logging
from fastapi import APIRouter
from fastapi import status
from utility.model import SearchQuerySchema
from fastapi_cache.decorator import cache
from utility.utils import search

logger = logging.getLogger(__name__)

router = APIRouter()

@cache(expire=60)
@router.post("/search", status_code=status.HTTP_200_OK)
async def perform_encrypted_search(search_parameters: SearchQuerySchema):
    return search(search_parameters)

