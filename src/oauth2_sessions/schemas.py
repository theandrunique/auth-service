from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.schemas import PyObjectId


class OAuth2SessionSchema(BaseModel):
    id: PyObjectId
    client_id: UUID
    scopes: list[str]
    last_refresh: datetime
    created_at: datetime
