from typing import Any
from uuid import UUID

from src.base_mongo_repository import BaseMongoRepository
from src.schemas import PyObjectId


class OAuth2SessionsRepository(BaseMongoRepository[PyObjectId]):
    async def get_by_jti(self, jti: UUID) -> dict[str, Any] | None:
        return await self.collection.find_one({"refresh_token_id": jti})
