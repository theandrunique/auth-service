import json

from redis.asyncio import Redis

from src.redis.client import pool

from .config import settings
from .schemas import AuthorizationRequest


class AuthorizationRequestsRepository:
    async def add(self, key: str, item: AuthorizationRequest) -> None:
        redis = Redis(connection_pool=pool)
        await redis.set(
            key, json.dumps(item.dump()), ex=settings.AUTHORIZATION_CODE_EXPIRE_SECONDS
        )

    async def get(self, key: str) -> AuthorizationRequest | None:
        redis = Redis(connection_pool=pool)
        data = await redis.get(key)
        if not data:
            return None
        await redis.delete(key)
        return AuthorizationRequest.from_dict(json.loads(data))
