from datetime import datetime

from pydantic import BaseModel, Field


class SessionSchema(BaseModel):
    jti: str = Field(..., serialization_alias="session_id")
    created_at: datetime
    last_accessed: datetime
    ip_address: str | None = None


class UserSessions(BaseModel):
    user_sessions: list[SessionSchema]
