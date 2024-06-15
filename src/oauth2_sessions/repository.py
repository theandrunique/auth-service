from typing import Any
from uuid import UUID

from src.base_mongo_repository import BaseMongoRepository
from src.oauth2.config import settings
from src.schemas import PyObjectId


class OAuth2SessionsRepository(BaseMongoRepository[PyObjectId]):
    async def get_by_jti(self, jti: UUID) -> dict[str, Any] | None:
        return await self.collection.find_one({"refresh_token_id": jti})

    async def init(self) -> None:
        await self.collection.create_index("refresh_token_id", unique=True)
        await self.collection.create_index(
            "last_refreshed",
            expireAfterSeconds=settings.REFRESH_TOKEN_EXPIRE_HOURS * 60 * 60,
        )
