from fastapi import APIRouter
from app.resources import search, index, user

api_version = "v1"

api_router = APIRouter()
api_router.include_router(search.router, prefix=f"/{api_version}", tags=["Search Endpoints"])
api_router.include_router(index.router, prefix=f"/{api_version}", tags=["Index Endpoints"])
api_router.include_router(user.router, prefix=f"/{api_version}/user", tags=["User Information Endpoints"])
