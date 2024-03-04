from datetime import datetime, timedelta
from enum import Enum

from config import settings
from pydantic import BaseModel, EmailStr, Field


class TokenType(Enum):
    REFRESH = "refresh"
    ACCESS = "access"


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    scope: list[str] = []
    token_type: str = "Bearer"
    expires_in: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    expires_at: int = Field(
        default_factory=lambda: int(
            (
                datetime.utcnow()
                + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            ).timestamp()
        )
    )


class TokenPayload(BaseModel):
    sub: int
    scopes: list[str]
    jti: str
    token_id: int


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    active: bool


class AuthSchema(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    email: EmailStr
    password: str = Field(
        min_length=3,
    )


class NewPasswordSchema(BaseModel):
    token: str
    new_password: str = Field(
        min_length=3,
    )


class OtpAuthSchema(BaseModel):
    email: EmailStr
    scopes: list[str]
    key: str
    otp: str
