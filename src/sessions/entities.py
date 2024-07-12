from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(kw_only=True)
class Session:
    id: UUID | None = None
    user_id: UUID
    last_used: datetime
    ip_address: str
    expires_at: datetime
