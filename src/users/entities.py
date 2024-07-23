from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(kw_only=True)
class UserFields:
    username: str
    email: str
    email_verified: bool
    image_url: str | None = None
    hashed_password: bytes
    active: bool
    created_at: datetime


@dataclass(kw_only=True)
class User(UserFields):
    id: UUID
