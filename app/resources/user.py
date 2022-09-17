import logging
from fastapi import APIRouter
from fastapi import status, Body
from fastapi_cache.decorator import cache
from utility.utils import (
    extract_user_info_from_lens, 
    fetch_follower_list
)

logger = logging.getLogger(__name__)

router = APIRouter()

@cache(expire=60)
@router.post("/info", status_code=status.HTTP_200_OK)
def get_user_metadata_by_wallet_address(wallet_address: str = Body(..., embed=True)):
    return extract_user_info_from_lens(wallet_address)

@cache(expire=60)
@router.post("/followers", status_code=status.HTTP_200_OK)
def get_user_followers_list(user_lens_id: str = Body(..., embed=True)):
    return fetch_follower_list(user_lens_id)