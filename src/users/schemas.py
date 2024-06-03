import datetime
import re
from uuid import UUID, uuid4

from pydantic import (
    AliasChoices,
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)

from src.users.config import settings

from .exceptions import PasswordValidationError


class UserPublic(BaseModel):
    id: UUID = Field(validation_alias=AliasChoices("_id", "id"))
    username: str
    email: EmailStr
    email_verified: bool
    active: bool
    created_at: datetime.datetime


class UserSchema(BaseModel):
    id: UUID = Field(validation_alias=AliasChoices("_id", "id"))
    username: str
    email: EmailStr
    email_verified: bool
    hashed_password: bytes
    active: bool
    created_at: datetime.datetime


class UserCreate(BaseModel):
    id: UUID = Field(default_factory=lambda: uuid4(), serialization_alias="_id")
    username: str
    email: EmailStr
    email_verified: bool = Field(default=False)
    hashed_password: bytes
    active: bool = Field(default=True)
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


class RegistrationSchema(BaseModel):
    username: str = Field(
        min_length=settings.USERNAME_MIN_LENGTH,
        max_length=settings.USERNAME_MAX_LENGTH,
        pattern=settings.USERNAME_PATTERN,
    )
    email: EmailStr
    password: str = Field(
        min_length=settings.PASSWORD_MIN_LENGTH,
        max_length=settings.PASSWORD_MAX_LENGTH,
    )

    @field_validator("password")
    @classmethod
    def check_pattern(cls, v: str) -> str:
        if not re.match(settings.PASSWORD_PATTERN, v):
            raise PasswordValidationError()
        return v


class ResetPasswordSchema(BaseModel):
    password: str = Field(
        min_length=settings.PASSWORD_MIN_LENGTH,
        max_length=settings.PASSWORD_MAX_LENGTH,
    )

    @field_validator("password")
    @classmethod
    def check_pattern(cls, v: str) -> str:
        if not re.match(settings.PASSWORD_PATTERN, v):
            raise PasswordValidationError()
        return v


class SearchResult(BaseModel):
    result: list[UserPublic]
    total: int
