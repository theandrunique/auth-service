from datetime import UTC, datetime
from uuid import UUID

from src.mongo import BaseMongoRepository


class SessionsRepository(BaseMongoRepository[UUID]):
    async def delete_expired_sessions(self) -> int:
        now = datetime.now(UTC)
        result = await self.collection.delete_many(
            {"expires_at": {"$lt": now}},
        )
        return result.deleted_count

    async def delete_except(self, except_id: UUID) -> int:
        result = await self.collection.delete_many(
            {"_id": {"$ne": except_id}},
        )
        return result.deleted_count

    async def delete_all(self) -> None:
        await self.collection.drop_collection()
