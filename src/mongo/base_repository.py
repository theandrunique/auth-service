from abc import ABC
from dataclasses import dataclass
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument


@dataclass(kw_only=True)
class BaseMongoRepository[T](ABC):
    collection: AsyncIOMotorCollection

    async def add(self, item: dict[str, Any]) -> T:
        result = await self.collection.insert_one(item)
        return result.inserted_id

    async def get_many(self, count: int, offset: int) -> list[dict[str, Any]]:
        result = await self.collection.find().skip(offset).to_list(length=count)
        return result

    async def get(self, id: T) -> dict[str, Any] | None:
        return await self.collection.find_one({"_id": id})

    async def update(
        self,
        id: T,
        new_values: dict[str, Any],
    ) -> dict[str, Any]:
        updated: dict[str, Any] = await self.collection.find_one_and_update(
            {"_id": id},
            {"$set": new_values},
            return_document=ReturnDocument.AFTER,
        )
        return updated

    async def delete(self, id: T) -> int:
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count
