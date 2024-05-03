from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from .client import pool


def get_redis_client() -> Generator[Redis, None, None]:
    redis = Redis(connection_pool=pool, decode_responses=True)
    yield redis


RedisClient = Annotated[Redis, Depends(get_redis_client)]
