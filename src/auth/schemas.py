import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)

from src.config import settings


class TokenPayload(BaseModel):
    sub: UUID
    jti: UUID
    exp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=settings.USER_TOKEN_EXPIRE_HOURS),
    )


class Token(BaseModel):
    user_id: UUID
    token: str


class Login(BaseModel):
    login: str
    password: str
