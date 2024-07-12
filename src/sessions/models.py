from datetime import datetime
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field

from src.sessions.entities import Session


class SessionODM(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    user_id: UUID
    last_used: datetime
    ip_address: str
    expires_at: datetime

    @classmethod
    def from_entity(cls, entity: "Session") -> "SessionODM":
        return cls(
            user_id=entity.user_id,
            last_used=entity.last_used,
            ip_address=entity.ip_address,
            expires_at=entity.expires_at,
        )

    def to_entity(self) -> "Session":
        return Session(
            id=self.id,
            user_id=self.user_id,
            last_used=self.last_used,
            ip_address=self.ip_address,
            expires_at=self.expires_at,
        )
