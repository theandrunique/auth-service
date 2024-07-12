from enum import Enum

from pydantic import BaseModel

from src.apps.dto import OAuth2AppInfoDTO
from src.users.entities import User


class AuthorizationRequest(BaseModel):
    application: OAuth2AppInfoDTO
    requested_scopes: list[str]
    redirect_uri: str
    user: User
    state: str | None = None
    nonce: str | None = None
    code_challenge: str | None = None
    code_challenge_method: str | None = None
    prompt: str | None = None


class ResponseType(str, Enum):
    code = "code"
    web_message = "web_message"
    token = "token"


class GrantType(str, Enum):
    authorization_code = "authorization_code"
    refresh_token = "refresh_token"


class CodeChallengeMethod(str, Enum):
    s256 = "S256"
