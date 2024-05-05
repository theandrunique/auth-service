import secrets

from pydantic import ValidationError

from src import jwt_token

from .config import settings
from .schemas import OAuth2AccessTokenPayload, OAuth2RefreshTokenPayload


def gen_authorization_code() -> str:
    return secrets.token_urlsafe(settings.AUTHORIZATION_CODE_LENGTH)


def gen_oauth_token(
    payload: OAuth2AccessTokenPayload | OAuth2RefreshTokenPayload,
) -> str:
    return jwt_token.create(payload=payload.model_dump())


def validate_access_token(token: str) -> OAuth2AccessTokenPayload | None:
    payload = jwt_token.decode(token)
    if not payload:
        return None
    try:
        return OAuth2AccessTokenPayload(**payload)
    except ValidationError:
        return None


def validate_refresh_token(token: str) -> OAuth2RefreshTokenPayload | None:
    payload = jwt_token.decode(token)
    if not payload:
        return None
    try:
        return OAuth2RefreshTokenPayload(**payload)
    except ValidationError:
        return None


def create_token_pair(
    payload: OAuth2AccessTokenPayload,
    refresh_payload: OAuth2RefreshTokenPayload,
) -> tuple[str, str]:
    access_token = gen_oauth_token(payload)
    refresh_token = gen_oauth_token(refresh_payload)
    return access_token, refresh_token
