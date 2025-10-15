import logging

import redis.asyncio as aioredis
from redis.asyncio import Redis

from fastapi_application.core.config import settings

logger = logging.getLogger(__name__)


class AsyncRedisClient:
    _client: Redis = None

    @classmethod
    async def initialize(cls):

        if cls._client is None:
            cls._client = await aioredis.from_url(
                f"redis://:{settings.redis.password}@{settings.redis.host}:{settings.redis.port}",
                max_connections=20,
                encoding="utf8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
        return cls._client

    @classmethod
    async def get_client(cls):
        if cls._client is None:
            await cls.initialize()
        return cls._client


async def set_async_redis_client() -> Redis:
    client = await AsyncRedisClient.initialize()
    logger.info("AsyncRedisClient is setting...")
    return client
