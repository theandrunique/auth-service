from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(kw_only=True)
class OAuth2Session:
    id: UUID | None = None
    user_id: UUID
    client_id: UUID
    token_id: UUID
    scopes: list[str]
    last_refresh: datetime
    created_at: datetime
