from typing import Any
from uuid import UUID

from src.base_mongo_repository import BaseMongoRepository


class AppsRepository(BaseMongoRepository[UUID]):
    async def get_by_client_id(self, client_id: UUID) -> dict[str, Any] | None:
        return await self.collection.find_one({"client_id": client_id})
