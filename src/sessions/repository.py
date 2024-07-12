from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.sessions.models import SessionODM

from .entities import Session


class ISessionsRepository(ABC):
    @abstractmethod
    async def add(self, session: Session) -> Session: ...

    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> Session | None: ...

    @abstractmethod
    async def update_last_used(self, session_id: UUID, last_used: datetime) -> None: ...

    @abstractmethod
    async def delete_session(self, session_id: UUID) -> Session | None: ...

    @abstractmethod
    async def delete_all_session_by_user_id(self, user_id: UUID) -> None: ...


class MongoSessionsRepository(ISessionsRepository):
    async def add(self, session: Session) -> Session:
        session_model = SessionODM.from_entity(session)
        await session_model.insert()
        return session_model.to_entity()

    async def get_by_id(self, session_id: UUID) -> Session | None:
        session_model = await SessionODM.find_one(SessionODM.id == session_id)
        if session_model is None:
            return None
        return session_model.to_entity()

    async def update_last_used(self, session_id: UUID, last_used: datetime) -> None:
        session = await SessionODM.find_one(SessionODM.id == session_id)
        if session is None:
            raise Exception("Session not found")

        session.last_used = last_used
        await session.save()

    async def delete_session(self, session_id: UUID) -> None:
        session = await SessionODM.find_one(SessionODM.id == session_id)
        if session is None:
            raise Exception("Session not found")

        await session.delete()

    async def delete_all_session_by_user_id(self, user_id: UUID) -> None:
        await SessionODM.find_many(SessionODM.user_id == user_id).delete()
