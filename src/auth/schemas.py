import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.config import settings
from src.users.exceptions import PasswordValidationError, UsernameValidationError


class LoginReq(BaseModel):
    login: str
    password: str


class RegistrationSchema(BaseModel):
    username: str = Field(
        max_length=settings.USERNAME_MAX_LENGTH,
        min_length=settings.USERNAME_MIN_LENGTH,
    )
    email: EmailStr
    password: str = Field(
        max_length=settings.PASSWORD_MAX_LENGTH,
        min_length=settings.PASSWORD_MIN_LENGTH,
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if not re.match(settings.USERNAME_PATTERN, value):
            raise UsernameValidationError
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not re.match(settings.PASSWORD_PATTERN, value):
            raise PasswordValidationError
        return value
