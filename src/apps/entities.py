from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(kw_only=True)
class Application:
    id: UUID | None = None
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
