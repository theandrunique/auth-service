from typing import Any
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import ReturnDocument

from src.mongo import Repository, db

from .schemas import OAuth2SessionCreate, OAuth2SessionSchema


class OAuth2SessionsRepository(Repository):
    def __init__(self, session: AsyncIOMotorClientSession, user_id: UUID) -> None:
        self.session = session
        self.collection = db[f"oauth2_sessions_{user_id}"]

    async def add(self, item: OAuth2SessionCreate) -> OAuth2SessionSchema:
        result = await self.collection.insert_one(
            item.model_dump(by_alias=True),
            session=self.session,
        )
        assert result.acknowledged
        return OAuth2SessionSchema(**item.model_dump())

    async def get_many(self, count: int, offset: int) -> list[OAuth2SessionSchema]:
        result = (
            await self.collection.find(session=self.session)
            .skip(offset)
            .to_list(length=count)
        )
        return [OAuth2SessionSchema(**item) for item in result]

    async def get(self, id: UUID) -> OAuth2SessionSchema | None:
        found = await self.collection.find_one(
            {"_id": id},
            session=self.session,
        )
        if found:
            return OAuth2SessionSchema(**found)
        return None

    async def get_by_jti(self, jti: UUID) -> OAuth2SessionSchema | None:
        found = await self.collection.find_one(
            {"refresh_token_id": jti},
            session=self.session,
        )
        if found:
            return OAuth2SessionSchema(**found)
        return None

    async def update(self, id: UUID, new_values: dict[str, Any]) -> OAuth2SessionSchema:
        updated = await self.collection.find_one_and_update(
            {"_id": id},
            {"$set": new_values},
            return_document=ReturnDocument.AFTER,
            session=self.session,
        )
        return OAuth2SessionSchema(**updated)

    async def update_jti(self, id: UUID, new_jti: UUID) -> OAuth2SessionSchema:
        return await self.update(id=id, new_values={"refresh_token_id": new_jti})

    async def delete(self, id: UUID) -> int:
        result = await self.collection.delete_one({"_id": id}, session=self.session)
        return result.deleted_count
