from dataclasses import dataclass
from typing import Any
from uuid import UUID

from src.services.base.hash import Hash
from src.users.repository import UsersRepository
from src.users.schemas import RegistrationSchema, UserCreate, UserPublic, UserSchema


@dataclass(kw_only=True)
class UsersService:
    repository: UsersRepository
    hash_service: Hash

    async def add(self, item: RegistrationSchema) -> UserSchema:
        new_user = UserCreate(
            username=item.username,
            email=item.email,
            hashed_password=self.hash_service.create(item.password),
        )
        await self.repository.add(new_user.model_dump(by_alias=True))
        return UserSchema(**new_user.model_dump())

    async def get_many(self, user_ids: list[UUID]) -> list[UserPublic]:
        users = await self.repository.get_users_by_ids(user_ids)
        return [UserPublic(**user) for user in users]

    async def get(self, id: UUID) -> UserSchema | None:
        found_user = await self.repository.get(id=id)
        if found_user:
            return UserSchema(**found_user)
        return None

    async def get_by_email(self, email: str) -> UserSchema | None:
        found_user = await self.repository.get_by_email(email)
        if found_user:
            return UserSchema(**found_user)
        return None

    async def get_by_username(self, username: str) -> UserSchema | None:
        found_user = await self.repository.get_by_username(username)
        if found_user:
            return UserSchema(**found_user)
        return None

    async def get_by_email_or_username(
        self, email_or_username: str
    ) -> UserSchema | None:
        found_user = await self.repository.get_by_email_or_username(email_or_username)
        if found_user:
            return UserSchema(**found_user)
        return None

    async def search_by_username(self, username: str) -> list[UserPublic] | None:
        found_users = await self.repository.search_by_username(username)
        if not found_users:
            return None
        return [UserPublic(**found_user) for found_user in found_users]

    async def update(self, id: UUID, new_values: dict[str, Any]) -> UserSchema:
        updated = await self.repository.update(id, new_values)
        return UserSchema(**updated)

    async def update_password(self, id: UUID, new_password: str) -> None:
        await self.repository.update(
            id, {"password": self.hash_service.create(new_password)}
        )

    async def verify_email(self, id: UUID) -> None:
        await self.repository.update(id, {"email_verified": True})

    async def delete(self, id: UUID) -> int:
        return await self.repository.delete(id)
