from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from src.config import settings
from src.sessions.dto import CreateSessionDTO
from src.sessions.entities import Session

from .repository import ISessionsRepository


def convert_create_session_dto_to_session(dto: CreateSessionDTO) -> Session:
    return Session(
        last_used=datetime.now(),
        ip_address=dto.ip_address,
        user_id=dto.user_id,
        expires_at=datetime.now() + timedelta(hours=settings.SESSION_EXPIRE_HOURS),
    )


class ISessionsService(ABC):
    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> Session | None: ...

    @abstractmethod
    async def create_new_session(self, dto: CreateSessionDTO) -> Session: ...

    @abstractmethod
    async def update_last_used(self, session_id: UUID) -> None: ...

    @abstractmethod
    async def delete(self, session_id: UUID) -> None: ...

    @abstractmethod
    async def delete_all_by_user_id(self, user_id: UUID) -> None: ...


@dataclass(kw_only=True)
class SessionsService(ISessionsService):
    repository: ISessionsRepository

    async def get_by_id(self, session_id: UUID) -> Session | None:
        return await self.repository.get_by_id(session_id)

    async def create_new_session(self, dto: CreateSessionDTO) -> Session:
        session = convert_create_session_dto_to_session(dto)
        return await self.repository.add(session)

    async def update_last_used(self, session_id: UUID) -> None:
        return await self.repository.update_last_used(session_id, datetime.now())

    async def delete(self, session_id: UUID) -> None:
        await self.repository.delete_session(session_id)

    async def delete_all_by_user_id(self, user_id: UUID) -> None:
        await self.repository.delete_all_session_by_user_id(user_id)
