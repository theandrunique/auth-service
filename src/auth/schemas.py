from datetime import datetime, timedelta
from enum import Enum

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)

from src.config import settings


class UserTokenPair(BaseModel):
    access_token: str
    refresh_token: str
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


class TokenType(Enum):
    REFRESH = "refresh"
    ACCESS = "access"


class UserAccessTokenPayload(BaseModel):
    id: int
    email: str


class UserRefreshTokenPayload(BaseModel):
    jti: str
    token_id: int


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    active: bool


class RegistrationSchema(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    email: EmailStr
    password: str = Field(
        min_length=3,
    )


class OtpAuthSchema(BaseModel):
    email: EmailStr
    otp: str


class OtpRequestSchema(BaseModel):
    email: EmailStr


class UserLoginSchema(BaseModel):
    login: str
    password: str


class RefreshToken(BaseModel):
    refresh_token: str

class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    token: str
    password: str = Field(
        min_length=3,
    )


class VerifyEmailSchema(BaseModel):
    token: str

