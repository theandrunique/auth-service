from typing import Any
from uuid import UUID

from src.base_mongo_repository import BaseMongoRepository
from src.schemas import PyObjectId


class AppsRepository(BaseMongoRepository[PyObjectId]):
    async def get_by_client_id(self, client_id: UUID) -> dict[str, Any] | None:
        return await self.collection.find_one({"client_id": client_id})

    async def init(self) -> None:
        await self.collection.create_index("client_id", unique=True)
