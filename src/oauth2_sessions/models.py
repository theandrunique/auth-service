from datetime import datetime
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field

from src.oauth2_sessions.entities import OAuth2Session, OAuth2SessionFields


class OAuth2SessionODM(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    user_id: UUID
    client_id: UUID
    token_id: UUID
    scopes: list[str]
    last_refresh: datetime
    created_at: datetime

    @classmethod
    def from_fields(cls, entity: "OAuth2SessionFields"):
        return cls(
            user_id=entity.user_id,
            client_id=entity.client_id,
            token_id=entity.token_id,
            scopes=entity.scopes,
            last_refresh=entity.last_refresh,
            created_at=entity.created_at,
        )

    def to_entity(self) -> "OAuth2Session":
        return OAuth2Session(
            id=self.id,
            user_id=self.user_id,
            client_id=self.client_id,
            token_id=self.token_id,
            scopes=self.scopes,
            last_refresh=self.last_refresh,
            created_at=self.created_at,
        )
