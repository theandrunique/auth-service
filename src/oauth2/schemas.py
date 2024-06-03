from dataclasses import asdict, dataclass
from datetime import datetime
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


class AccessTokenPayload(BaseModel):
    sub: UUID
    scopes: list[str]
    exp: datetime
    aud: str


class RefreshTokenPayload(BaseModel):
    sub: UUID
    jti: UUID
    exp: datetime
    aud: str


class CodeExchangeResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="Bearer")
    expires_in: int = Field(default=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    scopes: list[str]


class RefreshTokenRequest(BaseModel):
    refresh_token: str
    grant_type: str


@dataclass
class AuthorizationRequest:
    client_id: UUID
    client_secret: UUID
    requested_scopes: list[str]
    redirect_uri: str
    user: UserSchema
    state: str | None = None
    nonce: str | None = None
    code_challenge: str | None = None
    code_challenge_method: str | None = None
    prompt: str | None = None

    def dump(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuthorizationRequest":
        return cls(**data)
