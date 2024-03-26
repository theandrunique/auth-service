from typing import Any
from uuid import UUID

from pymongo import ReturnDocument

from src.mongo_helper import db

from .schemas import AppInMongo

app_collection = db["apps"]


class AppsRegistry:
    @staticmethod
    async def add(app: AppInMongo) -> UUID:
        result = await app_collection.insert_one(app.model_dump(by_alias=True))
        # inserted_id - should be UUID
        return result.inserted_id  # type: ignore

    @staticmethod
    async def get(app_id: UUID) -> AppInMongo | None:
        found_app = await app_collection.find_one({"_id": app_id})
        if found_app:
            return AppInMongo(**found_app)
        return None

    @staticmethod
    async def get_by_client_id(client_id: UUID) -> AppInMongo | None:
        found_app = await app_collection.find_one({"client_id": client_id})
        if found_app:
            return AppInMongo(**found_app)
        return None

    @staticmethod
    async def delete(app_id: UUID) -> int:
        result = await app_collection.delete_one({"_id": app_id})
        return result.deleted_count

    @staticmethod
    async def update(app_id: UUID, new_values: dict[str, Any]) -> AppInMongo:
        updated_app = await app_collection.find_one_and_update(
            {"_id": app_id},
            {"$set": new_values},
            return_document=ReturnDocument.AFTER,
        )
        return AppInMongo(**updated_app)

    @staticmethod
    async def update_optional(
        app_id: UUID, new_values: dict[str, Any]
    ) -> AppInMongo | None:
        updated_app = await app_collection.find_one_and_update(
            {"_id": app_id},
            {"$set": new_values},
            return_document=ReturnDocument.AFTER,
        )
        if updated_app:
            return AppInMongo(**updated_app)
        return None
