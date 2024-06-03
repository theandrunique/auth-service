import secrets
from uuid import UUID

from pydantic import ValidationError

from src import jwt_token
from src.oauth2.factories import AccessTokenPayloadFactory, RefreshTokenPayloadFactory

from .config import settings
from .schemas import AccessTokenPayload, RefreshTokenPayload


def gen_authorization_code() -> str:
    return secrets.token_urlsafe(settings.AUTHORIZATION_CODE_LENGTH)


def gen_oauth_token(
    payload: RefreshTokenPayloadFactory | AccessTokenPayloadFactory,
) -> str:
    return jwt_token.create(payload=payload.dump())


def validate_access_token(token: str) -> AccessTokenPayload | None:
    payload = jwt_token.decode(token)
    if not payload:
        return None
    try:
        return AccessTokenPayload(**payload)
    except ValidationError:
        return None


def validate_refresh_token(token: str) -> RefreshTokenPayload | None:
    payload = jwt_token.decode(token)
    if not payload:
        return None
    try:
        return RefreshTokenPayload(**payload)
    except ValidationError:
        return None


def create_token_pair(
    sub: UUID,
    scopes: list[str],
    aud: str,
) -> tuple[str, str, UUID]:
    access_payload = AccessTokenPayloadFactory(sub=sub, scopes=scopes, aud=aud)
    refresh_payload = RefreshTokenPayloadFactory(sub=sub)

    access_token = gen_oauth_token(access_payload)
    refresh_token = gen_oauth_token(refresh_payload)
    return access_token, refresh_token, refresh_payload.jti
