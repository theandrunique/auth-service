from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, field_validator

from .config import settings


class EmailTokenPayloadValidator(BaseModel):
    sub: UUID
    jti: UUID
    exp: datetime
    aud: str

    @field_validator("aud")
    @classmethod
    def check_type(cls, v: str) -> str:
        if v != "email":
            raise ValueError
        return v


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseEmailTokenPayload:
    sub: UUID
    jti: UUID = field(default_factory=lambda: uuid4())
    exp: datetime
    aud: str = field(default="email")


@dataclass(frozen=True, slots=True, kw_only=True)
class VerificationTokenPayload(BaseEmailTokenPayload):
    exp: datetime = field(
        default_factory=lambda: datetime.now()
        + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS)
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class ResetPasswordTokenPayload(BaseEmailTokenPayload):
    exp: datetime = field(
        default_factory=lambda: datetime.now()
        + timedelta(hours=settings.RESET_TOKEN_EXPIRE_HOURS)
    )


class EmailToken(BaseModel):
    token: str


class EmailRequest(BaseModel):
    email: EmailStr
