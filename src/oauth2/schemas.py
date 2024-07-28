from pydantic import BaseModel

from src.schemas import Scope


class CodeExchangeResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    scopes: list[str]


class RefreshTokenRequest(BaseModel):
    refresh_token: str
    grant_type: str


class OAuthRequestValidateResponseSchema(BaseModel):
    scopes: list[Scope]
