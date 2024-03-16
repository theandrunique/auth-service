from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SessionSchema(BaseModel):
    session_id: UUID = Field(..., serialization_alias="session_id")
    last_used: datetime
    ip_address: str | None = None
    expires_at: datetime


class UserSessions(BaseModel):
    user_sessions: list[SessionSchema]
