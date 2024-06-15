import re
from typing import Any
from uuid import UUID

from src.base_mongo_repository import BaseMongoRepository


class UsersRepository(BaseMongoRepository[UUID]):
    async def get_users_by_ids(self, user_ids: list[UUID]) -> list[dict[str, Any]]:
        return await self.collection.find({"_id": {"$in": user_ids}}).to_list(None)

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

    async def search_by_username(self, username: str) -> list[dict[str, Any]] | None:
        regex = re.compile(f"{re.escape(username)}", re.IGNORECASE)
        return await self.collection.find({"username": regex}).to_list(None)

    async def init(self) -> None:
        await self.collection.create_index("username", unique=True)
        await self.collection.create_index("email", unique=True)
