from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.users.schemas import UserSchema

from .config import settings


class ResponseType(str, Enum):
    code: str = "code"
    web_message: str = "web_message"
    token: str = "token"


class GrantType(str, Enum):
    authorization_code: str = "authorization_code"
    refresh_token: str = "refresh_token"


class CodeChallengeMethod(str, Enum):
    s256 = "S256"


class RedirectUriResponse(BaseModel):
    redirect_uri: str


class CodeExchangeResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="Bearer")
    expires_in: int = Field(default=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    scopes: list[str]


class WebMessageResponse(BaseModel):
    code: str
    state: str | None


class AccessTokenPayload(BaseModel):
    sub: UUID
    scopes: list[str]
    exp: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
        + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    )
    aud: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
    grant_type: str


class AuthorizationRequest(BaseModel):
    client_id: UUID
    client_secret: UUID
    requested_scopes: list[str]
    redirect_uri: str
    user: UserSchema
    state: str | None = None
    nonce: str | None = None
    code_challenge: str | None = None
    code_challenge_method: CodeChallengeMethod | None = None
    prompt: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuthorizationRequest":
        return cls(**data)
