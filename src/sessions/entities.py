from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(kw_only=True)
class SessionFields:
    user_id: UUID
    last_used: datetime
    ip_address: str
    expires_at: datetime


@dataclass(kw_only=True)
class Session(SessionFields):
    id: UUID
