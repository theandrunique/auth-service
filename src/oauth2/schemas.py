import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from .config import settings


class OAuth2AuthorizeRequest(BaseModel):
    client_id: UUID
    redirect_uri: str
    response_type: str
    scopes: list[str]
    state: str | None = Field(default=None)
    nonce: str | None = Field(default=None)


class OAuth2CodeExchangeRequest(BaseModel):
    client_id: UUID
    client_secret: UUID
    code: str


class OAuth2AuthorizeResponse(BaseModel):
    code: str
    state: str | None


class OAuth2AccessTokenPayload(BaseModel):
    sub: str
    scopes: list[str]
    exp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now()
        + datetime.timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    )


class OAuth2CodeExchangeResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="Bearer")
    expires_in: int = Field(default=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    scope: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
    grant_type: str

    @field_validator("grant_type")
    @classmethod
    def check_grant_type(cls, v: str) -> str:
        if v != "refresh_token":
            raise ValueError("grant_type must be 'refresh_token'")
        return v
