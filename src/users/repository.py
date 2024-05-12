from typing import Any
from uuid import UUID

from src.mongo import BaseMongoRepository


class UsersRepository(BaseMongoRepository[UUID]):
    async def get_by_email(self, email: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"email": email})

    async def get_by_username(self, username: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"username": username})

    async def get_by_email_or_username(
        self, email_or_username: str
    ) -> dict[str, Any] | None:
        return await self.collection.find_one(
            {"$or": [{"email": email_or_username}, {"username": email_or_username}]},
        )
