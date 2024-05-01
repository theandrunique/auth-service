from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import ReturnDocument

from src.mongo import Repository, db
from src.sessions.schemas import SessionCreate, SessionSchema


class SessionsRepository(Repository):
    def __init__(self, session: AsyncIOMotorClientSession, user_id: UUID) -> None:
        self.session = session
        self.collection = db[f"sessions_{user_id}"]

    async def add(self, item: SessionCreate) -> SessionSchema:
        result = await self.collection.insert_one(
            item.model_dump(by_alias=True),
            session=self.session,
        )
        assert result.acknowledged
        return SessionSchema(**item.model_dump())

    async def get_many(self, count: int, offset: int) -> list[SessionSchema]:
        result = (
            await self.collection.find(session=self.session)
            .skip(offset)
            .to_list(length=count)
        )
        return [SessionSchema(**item) for item in result]

    async def get(self, id: UUID) -> SessionSchema | None:
        found = await self.collection.find_one(
            {"_id": id},
            session=self.session,
        )
        if found:
            return SessionSchema(**found)
        return None

    async def update(self, id: UUID, new_values: dict[str, Any]) -> SessionSchema:
        updated = await self.collection.find_one_and_update(
            {"_id": id},
            {"$set": new_values},
            return_document=ReturnDocument.AFTER,
            session=self.session,
        )
        return SessionSchema(**updated)

    async def delete(self, id: UUID) -> int:
        result = await self.collection.delete_one({"_id": id}, session=self.session)
        return result.deleted_count

    async def delete_expired_sessions(self) -> int:
        now = datetime.now(UTC)

        result = await self.collection.delete_many(
            {"expires_at": {"$lt": now}},
            session=self.session,
        )

        return result.deleted_count

    async def delete_except(self, except_id: UUID) -> int:
        result = await self.collection.delete_many(
            {"_id": {"$ne": except_id}},
            session=self.session,
        )

        return result.deleted_count

    async def delete_all(self) -> None:
        await db.drop_collection(self.collection.name, session=self.session)

