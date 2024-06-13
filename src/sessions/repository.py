from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from src.base_mongo_repository import BaseMongoRepository


class SessionsRepository(BaseMongoRepository[UUID]):
    async def get_many_by_user(
        self, user_id: UUID, count: int, offset: int
    ) -> list[dict[str, Any]]:
        return (
            await self.collection.find({"user_id": user_id})
            .skip(offset)
            .to_list(length=count)
        )  # noqa: E501

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

    async def delete_all(self, user_id: UUID) -> None:
        await self.collection.delete_many({"user_id": user_id})
