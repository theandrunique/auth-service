from typing import Any
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import ReturnDocument

from src.auth.utils import hash_password
from src.mongo import Repository, db
from src.users.schemas import RegistrationSchema, UserCreate, UserSchema

users_collection = db["users"]


class UsersRepository(Repository):
    def __init__(self, session: AsyncIOMotorClientSession) -> None:
        self.session = session

    async def add(self, item: RegistrationSchema) -> UserSchema:
        new_user = UserCreate(
            username=item.username,
            email=item.email,
            hashed_password=hash_password(item.password),
        )
        result = await users_collection.insert_one(
            new_user.model_dump(by_alias=True),
            session=self.session,
        )
        assert result.acknowledged
        return UserSchema(**new_user.model_dump())

    async def get_many(self, count: int, offset: int) -> list[UserSchema]:
        raise NotImplementedError()

    async def get(self, id: UUID) -> UserSchema | None:
        found_user = await users_collection.find_one(
            {"_id": id},
            session=self.session,
        )
        if found_user:
            return UserSchema(**found_user)
        return None

    async def get_by_email(self, email: str) -> UserSchema | None:
        found_user = await users_collection.find_one(
            {"email": email},
            session=self.session,
        )
        if found_user:
            return UserSchema(**found_user)
        return None

    async def get_by_username(self, username: str) -> UserSchema | None:
        found_user = await users_collection.find_one(
            {"username": username},
            session=self.session,
        )
        if found_user:
            return UserSchema(**found_user)
        return None

    async def get_by_email_or_username(
        self, email_or_username: str
    ) -> UserSchema | None:
        found_user = await users_collection.find_one(
            {"$or": [{"email": email_or_username}, {"username": email_or_username}]},
            session=self.session,
        )
        if found_user:
            return UserSchema(**found_user)
        return None

    async def update(self, id: UUID, new_values: dict[str, Any]) -> UserSchema:
        updated = await users_collection.find_one_and_update(
            {"_id": id},
            {"$set": new_values},
            return_document=ReturnDocument.AFTER,
            session=self.session,
        )
        if updated:
            return UserSchema(**updated)
        return None

    async def update_password(self, new_password: str, id: UUID) -> None:
        await users_collection.update_one(
            {"_id": id},
            {"$set": {"password": hash_password(new_password)}},
            session=self.session,
        )

    async def verify_email(self, id: UUID) -> None:
        await users_collection.update_one(
            {"_id": id},
            {"$set": {"email_verified": True}},
            session=self.session,
        )

    async def delete(self, id: UUID) -> int:
        result = await users_collection.delete_one({"_id": id}, session=self.session)
        return result.deleted_count
