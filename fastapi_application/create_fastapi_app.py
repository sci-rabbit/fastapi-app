import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_limiter import FastAPILimiter

from core.db import dispose
from error_handlers import register_errors_handlers
from middleware import CorrelationIdMiddleware
from redis_conf.redis import set_async_redis_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application started")
    redis_client = await set_async_redis_client()
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    await FastAPILimiter.init(redis_client)
    yield
    await dispose()
    logger.info("Application stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    register_errors_handlers(app)
    app.add_middleware(CorrelationIdMiddleware)
    return app
