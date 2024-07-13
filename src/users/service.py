from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.services.base.hash import Hash
from src.users.dto import RegisterUserDTO, UpdateUserPasswordDTO
from src.users.entities import User, UserFields
from src.users.repository import IUsersRepository


class IUsersService(ABC):
    @abstractmethod
    async def register_new_user(self, dto: RegisterUserDTO) -> User: ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> User | None: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def get_user_by_email_or_username(self, email_or_username: str) -> User | None: ...

    @abstractmethod
    async def update_password(self, dto: UpdateUserPasswordDTO) -> None: ...

    @abstractmethod
    async def deactivate_user(self, id: UUID) -> None: ...


@dataclass
class UsersService(IUsersService):
    repository: IUsersRepository
    hash_service: Hash

    async def register_new_user(self, dto: RegisterUserDTO) -> User:
        new_user = await self.repository.add(
            UserFields(
                username=dto.username,
                email=dto.email,
                email_verified=False,
                hashed_password=self.hash_service.create(dto.password),
                image_url=None,
                active=True,
                created_at=datetime.now(),
            )
        )

        return new_user

    async def get_by_id(self, id: UUID) -> User | None:
        return await self.repository.get_by_id(id)

    async def get_by_username(self, username: str) -> User | None:
        return await self.repository.get_by_username(username)

    async def get_by_email(self, email: str) -> User | None:
        return await self.repository.get_by_email(email)

    async def get_user_by_email_or_username(self, email_or_username: str) -> User | None:
        if "@" in email_or_username:
            user = await self.get_by_email(email=email_or_username)
        else:
            user = await self.get_by_username(username=email_or_username)
        return user

    async def update_password(self, dto: UpdateUserPasswordDTO) -> None:
        await self.repository.update_password(
            id=dto.user_id,
            new_password_hash=self.hash_service.create(dto.new_password),
        )

    async def deactivate_user(self, id: UUID) -> None:
        await self.repository.change_active_status(id, new_status=False)
