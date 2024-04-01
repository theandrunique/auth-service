import re

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)

from src.users.config import settings

from .exceptions import PasswordValidationError


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    active: bool


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
