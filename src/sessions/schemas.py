from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


@dataclass
class SessionCookies:
    token: str


class SessionSchema(BaseModel):
    id: UUID
    last_used: datetime
    ip_address: str
    expires_at: datetime
