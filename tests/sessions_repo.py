from datetime import datetime
from uuid import UUID, uuid4

from src.sessions.entities import Session
from src.sessions.repository import ISessionsRepository


class InMemorySessionsRepository(ISessionsRepository):
    def __init__(self):
        self.sessions: dict[UUID, Session] = {}

    async def add(self, session: Session) -> Session:
        if session.id is None:
            session.id = uuid4()
        self.sessions[session.id] = session
        return session

    async def get_by_id(self, session_id: UUID) -> Session | None:
        return self.sessions.get(session_id)

    async def update_last_used(self, session_id: UUID, last_used: datetime) -> None:
        session = self.sessions[session_id]
        session.last_used = last_used

    async def delete_session(self, session_id: UUID) -> Session | None:
        return self.sessions.pop(session_id, None)

    async def delete_all_session_by_user_id(self, user_id: UUID) -> None:
        self.sessions = {k: v for k, v in self.sessions.items() if v.user_id != user_id}
