import secrets

import jwt

from .config import settings
from .schemas import OAuth2AccessTokenPayload, OAuth2RefreshTokenPayload


def gen_authorization_code() -> str:
    return secrets.token_urlsafe(settings.AUTHORIZATION_CODE_LENGTH)


def gen_access_token(payload: OAuth2AccessTokenPayload) -> str:
    return jwt.encode(
        payload=payload.model_dump(),
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def validate_access_token(token: str) -> OAuth2AccessTokenPayload:
    payload = jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    return OAuth2AccessTokenPayload(**payload)


def gen_refresh_token(payload: OAuth2RefreshTokenPayload) -> str:
    return jwt.encode(
        payload=payload.model_dump(),
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def validate_refresh_token(token: str) -> OAuth2RefreshTokenPayload:
    payload = jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    return OAuth2RefreshTokenPayload(**payload)


def create_token_pair(
    payload: OAuth2AccessTokenPayload,
    refresh_payload: OAuth2RefreshTokenPayload,
) -> tuple[str, str]:
    access_token = gen_access_token(payload)
    refresh_token = gen_refresh_token(refresh_payload)
    return access_token, refresh_token
