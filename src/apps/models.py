from datetime import datetime
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field

from src.apps.entities import Application


class AppODM(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    name: str
    client_id: UUID
    client_secret: UUID
    redirect_uris: list[str]
    scopes: list[str]
    creator_id: UUID
    description: str | None = None
    website: str | None = None
    created_at: datetime
    is_web_message_allowed: bool

    @classmethod
    def from_entity(cls, entity: "Application") -> "AppODM":
        return cls(
            name=entity.name,
            client_id=entity.client_id,
            client_secret=entity.client_secret,
            redirect_uris=entity.redirect_uris,
            scopes=entity.scopes,
            creator_id=entity.creator_id,
            description=entity.description,
            website=entity.website,
            created_at=entity.created_at,
            is_web_message_allowed=entity.is_web_message_allowed,
        )

    def to_entity(self) -> "Application":
        return Application(
            id=self.id,
            name=self.name,
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uris=self.redirect_uris,
            scopes=self.scopes,
            creator_id=self.creator_id,
            description=self.description,
            website=self.website,
            created_at=self.created_at,
            is_web_message_allowed=self.is_web_message_allowed,
        )
