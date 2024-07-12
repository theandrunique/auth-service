from abc import ABC, abstractmethod
from uuid import UUID

from src.users.models import UserODM

from .entities import User


class IUsersRepository(ABC):
    @abstractmethod
    async def add(self, user: User) -> User: ...

    @abstractmethod
    async def get_all(self, count: int, offset: int) -> list[User]: ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def update_username(self, id: UUID, new_username: str) -> User: ...

    @abstractmethod
    async def update_password(self, id: UUID, new_password_hash: bytes) -> User: ...

    @abstractmethod
    async def change_active_status(self, id: UUID, new_status: bool) -> User: ...


class MongoUsersRepository(IUsersRepository):
    async def add(self, user: User) -> User:
        user_model = UserODM.from_entity(user)
        await user_model.insert()
        return user_model.to_entity()

    async def get_all(self, count: int, offset: int) -> list[User]:
        users = await UserODM.find_all().skip(offset).limit(count).to_list()
        return [user.to_entity() for user in users]

    async def get_by_id(self, id: UUID) -> User | None:
        user = await UserODM.find_one(UserODM.id == id)
        return user.to_entity() if user else None

    async def get_by_email(self, email: str) -> User | None:
        user = await UserODM.find_one(UserODM.email == email)
        return user.to_entity() if user else None

    async def get_by_username(self, username: str) -> User | None:
        user = await UserODM.find_one(UserODM.username == username)
        return user.to_entity() if user else None

    async def update_username(self, id: UUID, new_username: str) -> User:
        user = await UserODM.find_one(UserODM.id == id)
        if user is None:
            raise Exception("User not found")

        user.username = new_username
        await user.save()
        return user.to_entity()

    async def update_password(self, id: UUID, new_password_hash: bytes) -> User:
        user = await UserODM.find_one(UserODM.id == id)
        if user is None:
            raise Exception("User not found")

        user.hashed_password = new_password_hash
        await user.save()
        return user.to_entity()

    async def change_active_status(self, id: UUID, new_status: bool) -> User:
        user = await UserODM.find_one(UserODM.id == id)
        if user is None:
            raise Exception("User not found")

        user.active = new_status
        await user.save()
        return user.to_entity()
