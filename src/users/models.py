from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from beanie import Document, Indexed
from pydantic import Field

from src.users.entities import User, UserFields


class UserODM(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    username: Annotated[str, Indexed(unique=True)]
    email: str
    email_verified: bool
    hashed_password: bytes
    image_url: str | None = Field(default=None)
    active: bool
    created_at: datetime

    @classmethod
    def from_fields(cls, entity: "UserFields") -> "UserODM":
        return cls(
            username=entity.username,
            email=entity.email,
            email_verified=entity.email_verified,
            hashed_password=entity.hashed_password,
            image_url=entity.image_url,
            active=entity.active,
            created_at=entity.created_at,
        )

    def to_entity(self) -> "User":
        return User(
            id=self.id,
            username=self.username,
            email=self.email,
            email_verified=self.email_verified,
            hashed_password=self.hashed_password,
            image_url=self.image_url,
            active=self.active,
            created_at=self.created_at,
        )
