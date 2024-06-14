from dataclasses import dataclass

import orjson
from redis.asyncio import Redis

from .config import settings
from .schemas import AuthorizationRequest


@dataclass(kw_only=True)
class AuthorizationRequestsRepository:
    redis: Redis

    async def add(self, key: str, item: AuthorizationRequest) -> None:
        await self.redis.set(
            key, item.model_dump_json(), ex=settings.AUTHORIZATION_CODE_EXPIRE_SECONDS
        )

    async def get(self, key: str) -> AuthorizationRequest | None:
        data = await self.redis.get(key)
        if not data:
            return None
        await self.redis.delete(key)
        return AuthorizationRequest(**orjson.loads(data))
