from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OAuth2SessionSchema(BaseModel):
    id: UUID
    client_id: UUID
    scopes: list[str]
    last_refresh: datetime
    created_at: datetime
