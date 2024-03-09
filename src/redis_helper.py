import redis.asyncio as aioredis

from src.config import settings

redis_client = aioredis.from_url(
    str(settings.REDIS_URL),  # type: ignore
    decode_responses=True,
)
