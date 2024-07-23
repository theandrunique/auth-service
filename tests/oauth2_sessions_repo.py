from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from src.oauth2_sessions.entities import OAuth2Session
from src.oauth2_sessions.repository import IOAuth2SessionsRepository


class InMemoryOAuth2SessionsRepository(IOAuth2SessionsRepository):
    def __init__(self):
        self.sessions: dict[UUID, OAuth2Session] = {}

    async def add(self, session: OAuth2Session) -> OAuth2Session:
        if session.id is None:
            session.id = uuid4()
        self.sessions[session.id] = session
        return session

    async def get_by_id(self, session_id: UUID) -> OAuth2Session | None:
        return self.sessions.get(session_id)

    async def get_by_token_id(self, jti: UUID) -> dict[str, Any] | None:
        session = next((s for s in self.sessions.values() if s.id == jti), None)
        return session.__dict__ if session else None

    async def update_token_id_and_last_refresh(self, session_id: UUID, token_id: UUID, last_refresh: datetime) -> None:
        session = self.sessions[session_id]
        session.id = token_id
        session.last_refresh = last_refresh

    async def delete_session(self, session_id: UUID) -> OAuth2Session | None:
        return self.sessions.pop(session_id, None)

    async def delete_sessions(self, user_id: UUID) -> None:
        self.sessions = {k: v for k, v in self.sessions.items() if v.user_id != user_id}
