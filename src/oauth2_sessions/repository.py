from typing import Any
from uuid import UUID

from src.mongo import BaseMongoRepository


class OAuth2SessionsRepository(BaseMongoRepository[UUID]):
    async def get_by_jti(self, jti: UUID) -> dict[str, Any] | None:
        return await self.collection.find_one({"refresh_token_id": jti})
