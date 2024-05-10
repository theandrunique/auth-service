import enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr

from .config import settings


class EmailAudience(str, enum.Enum):
    EMAIL_CONFIRMATION = "email-confirmation"
    RESET_PASSWORD = "email-reset-password"


class EmailTokenPayloadValidator(BaseModel):
    sub: UUID
    jti: UUID
    exp: datetime
    aud: EmailAudience


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseEmailTokenPayload:
    sub: UUID
    jti: UUID = field(default_factory=lambda: uuid4())
    exp: datetime
    aud: str


@dataclass(frozen=True, slots=True, kw_only=True)
class VerificationTokenPayload(BaseEmailTokenPayload):
    exp: datetime = field(
        default_factory=lambda: datetime.now()
        + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS)
    )
    aud: EmailAudience = EmailAudience.EMAIL_CONFIRMATION


@dataclass(frozen=True, slots=True, kw_only=True)
class ResetPasswordTokenPayload(BaseEmailTokenPayload):
    exp: datetime = field(
        default_factory=lambda: datetime.now()
        + timedelta(hours=settings.RESET_TOKEN_EXPIRE_HOURS)
    )
    aud: EmailAudience = EmailAudience.RESET_PASSWORD


class EmailToken(BaseModel):
    token: str


class EmailRequest(BaseModel):
    email: EmailStr
