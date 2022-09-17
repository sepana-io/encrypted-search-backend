import logging
from fastapi import FastAPI
from app.resources.controller import api_router
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from utility.redis_utils import get_redis_client
from utility.es_utils import es

logger = logging.getLogger(__name__)


def get_application() -> FastAPI:
    app = FastAPI(title="Sepana Search API", debug=True, version="1.0")
    app.include_router(api_router)

    @app.on_event("startup")
    async def sepana_startup_event():
        es.init_app()
        redis = get_redis_client()
        FastAPICache.init(RedisBackend(redis), prefix="sepana-cache")

    return app
