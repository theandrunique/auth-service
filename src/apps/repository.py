from typing import Any
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import ReturnDocument

from src.mongo import db

from .schemas import AppInMongo


class AppsRepository:
    def __init__(self, session: AsyncIOMotorClientSession) -> None:
        self.app_collection = db["apps"]
        self.session = session

    async def add(self, app: AppInMongo) -> UUID:
        result = await self.app_collection.insert_one(
            app.model_dump(by_alias=True),
            session=self.session,
        )
        # inserted_id - should be UUID
        return result.inserted_id  # type: ignore

    async def get(self, id: UUID) -> AppInMongo | None:
        found_app = await self.app_collection.find_one(
            {"_id": id},
            session=self.session,
        )
        if found_app:
            return AppInMongo(**found_app)
        return None

    async def get_many(self) -> list[AppInMongo]:
        raise NotImplementedError()

    async def get_by_client_id(self, client_id: UUID) -> AppInMongo | None:
        found_app = await self.app_collection.find_one(
            {"client_id": client_id}, session=self.session
        )
        if found_app:
            return AppInMongo(**found_app)
        return None

    async def update(self, id: UUID, new_values: dict[str, Any]) -> AppInMongo:
        updated_app = await self.app_collection.find_one_and_update(
            {"_id": id},
            {"$set": new_values},
            return_document=ReturnDocument.AFTER,
            session=self.session,
        )
        return AppInMongo(**updated_app)

    async def delete(self, id: UUID) -> int:
        result = await self.app_collection.delete_one({"_id": id}, session=self.session)
        return result.deleted_count


repository = AppsRepository()
