from dataclasses import dataclass
from typing import Any
from uuid import UUID

from .repository import OAuth2SessionsRepository
from .schemas import OAuth2SessionCreate, OAuth2SessionSchema


@dataclass(kw_only=True)
class OAuth2SessionsService:
    repository: OAuth2SessionsRepository

    async def add(self, item: OAuth2SessionCreate) -> OAuth2SessionSchema:
        await self.repository.add(item.model_dump(by_alias=True))
        return OAuth2SessionSchema(**item.model_dump())

    async def get_many(self, count: int, offset: int) -> list[OAuth2SessionSchema]:
        result = await self.repository.get_many(count, offset)
        return [OAuth2SessionSchema(**item) for item in result]

    async def get(self, id: UUID) -> OAuth2SessionSchema | None:
        found = await self.repository.get(id)
        if found:
            return OAuth2SessionSchema(**found)
        return None

    async def get_by_jti(self, jti: UUID) -> OAuth2SessionSchema | None:
        found = await self.repository.get_by_jti(jti)
        if found:
            return OAuth2SessionSchema(**found)
        return None

    async def update(self, id: UUID, new_values: dict[str, Any]) -> OAuth2SessionSchema:
        updated = await self.repository.update(id, new_values)
        return OAuth2SessionSchema(**updated)

    async def update_jti(self, id: UUID, new_jti: UUID) -> OAuth2SessionSchema:
        updated = await self.repository.update(
            id, new_values={"refresh_token_id": new_jti}
        )
        return OAuth2SessionSchema(**updated)

    async def delete(self, id: UUID) -> int:
        return await self.repository.delete(id)
