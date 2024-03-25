import re

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)

from src.config import settings

from .exceptions import PasswordValidationError


class UserTokenSchema(BaseModel):
    user_id: int
    token: str


class UserTokenPayload(BaseModel):
    user_id: int
    email: str
    jti: str


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    active: bool


class RegistrationSchema(BaseModel):
    username: str = Field(
        min_length=settings.USERS.USERNAME_MIN_LENGTH,
        max_length=settings.USERS.USERNAME_MAX_LENGTH,
        pattern=settings.USERS.USERNAME_PATTERN,
    )
    email: EmailStr
    password: str = Field(
        min_length=settings.USERS.PASSWORD_MIN_LENGTH,
        max_length=settings.USERS.PASSWORD_MAX_LENGTH,
    )

    @field_validator("password")
    @classmethod
    def check_pattern(cls, v: str) -> str:  # type: ignore
        if not re.match(settings.USERS.PASSWORD_PATTERN, v):
            raise PasswordValidationError()
        return v


class OtpRequestSchema(BaseModel):
    email: EmailStr


class UserLoginSchema(BaseModel):
    login: str
    password: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    password: str = Field(
        min_length=settings.USERS.PASSWORD_MIN_LENGTH,
        max_length=settings.USERS.PASSWORD_MAX_LENGTH,
    )

    @field_validator("password")
    @classmethod
    def check_pattern(cls, v: str) -> str:
        if not re.match(settings.USERS.PASSWORD_PATTERN, v):
            raise PasswordValidationError()
        return v
