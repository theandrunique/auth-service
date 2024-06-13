import json

from src.dependencies import Container, resolve

from .config import settings
from .schemas import AuthorizationRequest


class AuthorizationRequestsRepository:
    async def add(self, key: str, item: AuthorizationRequest) -> None:
        redis = resolve(Container.Redis)
        await redis.set(
            key, json.dumps(item.dump()), ex=settings.AUTHORIZATION_CODE_EXPIRE_SECONDS
        )

    async def get(self, key: str) -> AuthorizationRequest | None:
        redis = resolve(Container.Redis)
        data = await redis.get(key)
        if not data:
            return None
        await redis.delete(key)
        return AuthorizationRequest.from_dict(json.loads(data))
