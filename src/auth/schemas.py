import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)

from src.config import settings


class UserTokenPayload(BaseModel):
    sub: int
    jti: UUID
    exp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=settings.USER_TOKEN_EXPIRE_HOURS),
    )


class UserTokenSchema(BaseModel):
    user_id: int
    token: str


class LoginSchema(BaseModel):
    login: str
    password: str


class EmailRequest(BaseModel):
    email: EmailStr
