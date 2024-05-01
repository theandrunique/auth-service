from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from pydantic import AliasChoices, BaseModel, Field

from .config import settings


class SessionCreate(BaseModel):
    id: UUID = Field(
        default_factory=lambda: uuid4(),
        serialization_alias="_id",
    )
    last_used: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
        + timedelta(hours=settings.EXPIRE_HOURS)
    )
    ip_address: str | None = Field(default=None)


class SessionSchema(BaseModel):
    id: UUID = Field(validation_alias=AliasChoices("_id", "id"))
    last_used: datetime
    ip_address: str | None = None
    expires_at: datetime


class UserSessions(BaseModel):
    user_sessions: list[SessionSchema]
