import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from .config import settings


class OAuth2CodeExchangeRequest(BaseModel):
    code: str
    redirect_uri: str
    grant_type: str

    @field_validator("grant_type")
    @classmethod
    def check_grant_type(cls, v: str) -> str:
        if v != "authorization_code":
            raise ValueError("grant_type must be 'authorization_code'")
        return v


class OAuth2AuthorizeResponse(BaseModel):
    code: str
    state: str | None


class OAuth2AccessTokenPayload(BaseModel):
    sub: UUID
    scopes: list[str]
    exp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now()
        + datetime.timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    )
    typ: str = Field(default="access")

    @field_validator("typ")
    @classmethod
    def check_type(cls, v: str) -> str:
        if v != "access":
            raise ValueError("Invalid typ")
        return v


class OAuth2RefreshTokenPayload(BaseModel):
    sub: UUID
    jti: UUID = Field(default_factory=lambda: uuid4())
    exp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now()
        + datetime.timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)
    )
    typ: str = Field(default="refresh")

    @field_validator("typ")
    @classmethod
    def check_type(cls, v: str) -> str:
        if v != "refresh":
            raise ValueError("Invalid typ")
        return v


class OAuth2CodeExchangeResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="Bearer")
    expires_in: int = Field(default=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    scopes: list[str]


class RefreshTokenRequest(BaseModel):
    refresh_token: str
    grant_type: str

    @field_validator("grant_type")
    @classmethod
    def check_grant_type(cls, v: str) -> str:
        if v != "refresh_token":
            raise ValueError("grant_type must be 'refresh_token'")
        return v
