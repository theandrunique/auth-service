from abc import ABC, abstractmethod
from dataclasses import dataclass

from redis.asyncio import Redis

from src.config import settings
from src.oauth2.entities import AuthorizationRequest
from src.oauth2.exceptions import InvalidAuthorizationCode
from src.oauth2.utils import gen_authorization_code


class IAuthReqRepository(ABC):
    @abstractmethod
    async def add(self, key: str, req: AuthorizationRequest) -> None: ...

    @abstractmethod
    async def get(self, key: str) -> AuthorizationRequest | None: ...


@dataclass
class AuthorizationRequestsRepository(IAuthReqRepository):
    redis: Redis

    async def add(self, key: str, req: AuthorizationRequest) -> None:
        await self.redis.set(key, req.model_dump_json(), ex=settings.AUTHORIZATION_CODE_EXPIRE_SECONDS)

    async def get(self, key: str) -> AuthorizationRequest | None:
        data = await self.redis.get(key)
        if not data:
            return None
        await self.redis.delete(key)
        return AuthorizationRequest.model_validate_json(data)


class IAuthReqService(ABC):
    @abstractmethod
    async def get(self, code: str) -> AuthorizationRequest: ...

    @abstractmethod
    async def create_new_request(self, req: AuthorizationRequest) -> str: ...


@dataclass
class AuthReqService(IAuthReqService):
    repository: IAuthReqRepository

    async def get(self, code: str) -> AuthorizationRequest:
        req = await self.repository.get(code)
        if req is None:
            raise InvalidAuthorizationCode
        return req

    async def create_new_request(self, req: AuthorizationRequest) -> str:
        code = gen_authorization_code()
        await self.repository.add(code, req)
        return code
