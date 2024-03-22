import datetime
from uuid import UUID

from pydantic import BaseModel, Field

ACCESS_TOKEN_EXPIRE_SECONDS = 3600


class OAuth2AuthorizeRequest(BaseModel):
    client_id: UUID
    redirect_uri: str
    response_type: str
    scopes: list[str]
    state: str | None
    nonce: str | None


class OAuth2CodeExchangeRequest(BaseModel):
    client_id: UUID
    client_secret: UUID
    code: str


class OAuth2AuthorizeResponse(BaseModel):
    code: str
    state: str


class OAuth2AccessTokenPayload(BaseModel):
    sub: str
    scope: str
    exp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now()
        + datetime.timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    )


class OAuth2CodeExchangeResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="Bearer")
    expires_in: int
    scope: str
