import os

from redis.asyncio import Redis

from src.logger import logger

from .client import pool
from .config import settings


async def ping_redis() -> None:
    ping_success = False
    redis = Redis(connection_pool=pool)
    for i in range(settings.PING_ATTEMPTS):
        attempt_text = f"({i + 1} attempt)" if i > 0 else ""
        try:
            logger.info(f"Pinging Redis... {attempt_text}")
            await redis.ping()
            logger.info(
                f"Redis ping successful. "
                f"Connected to {redis.connection_pool.connection_kwargs}"
            )
            ping_success = True
            break
        except ConnectionError as e:
            logger.error(f"Failed to ping Redis. Error: {e}")

    if not ping_success:
        os._exit(1)


async def redis_info() -> None:
    redis = Redis(connection_pool=pool)
    info = await redis.info()
    logger.info(info)
