from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ValidationError

from src.exceptions import ServiceError, ServiceErrorCode

from .config import settings


@dataclass(kw_only=True)
class User:
    id: UUID | None = None
    username: str
    email: str
    email_verified: bool
    image_url: str | None = None
    hashed_password: bytes
    active: bool
    created_at: datetime

    def validate(self):
        try:
            UserValidator(
                username=self.username,
                email=self.email,
                email_verified=self.email_verified,
                image_url=self.image_url,
                hashed_password=self.hashed_password,
                active=self.active,
                created_at=self.created_at,
            )
        except ValidationError:
            raise ServiceError(
                code=ServiceErrorCode.INVALID_FORM_BODY,
            )


class UserValidator(BaseModel):
    username: str = Field(max_length=settings.USERNAME_MAX_LENGTH, min_length=settings.USERNAME_MIN_LENGTH)
    email: EmailStr
    email_verified: bool
    image_url: str | None = None
    hashed_password: bytes
    active: bool
    created_at: datetime
