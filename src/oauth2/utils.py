import base64
import hashlib
import secrets
from uuid import UUID, uuid4

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings as global_settings

from .config import settings
from .crud import OAuth2SessionsDB
from .models import OAuth2SessionsInDB
from .schemas import OAuth2AccessTokenPayload, OAuth2CodeExchangeResponse


def gen_authorization_code() -> str:
    return secrets.token_urlsafe(settings.AUTHORIZATION_CODE_LENGTH)


def align_b64(b64_string: str) -> str:
    missing = len(b64_string) % 4
    return f"{b64_string}{'=' * missing}"


def validate_token(token: str, token_hash: bytes) -> bool:
    b64_decoded = base64.urlsafe_b64decode(align_b64(token))
    input_hash = hashlib.sha256(b64_decoded)
    return secrets.compare_digest(input_hash.digest(), token_hash)


def gen_access_token(payload: OAuth2AccessTokenPayload) -> str:
    return jwt.encode(
        payload=payload.model_dump(),
        key=global_settings.SECRET_KEY,
        algorithm=global_settings.ALGORITHM,
    )


def gen_refresh_token_bytes() -> bytes:
    return secrets.token_bytes(settings.REFRESH_TOKEN_LENGTH)


def get_token_from_bytes(token_bytes: bytes) -> str:
    return base64.urlsafe_b64encode(token_bytes).rstrip(b"=").decode("utf-8")


def get_bytes_from_token(token: str) -> bytes:
    return base64.urlsafe_b64decode(align_b64(token))


def hash_token(token_bytes: bytes) -> bytes:
    return hashlib.sha256(token_bytes).digest()


def create_token_pair(
    payload: OAuth2AccessTokenPayload, refresh_token_bytes: bytes
) -> tuple[str, str]:
    access_token = gen_access_token(payload)
    refresh_token = get_token_from_bytes(refresh_token_bytes)
    return access_token, refresh_token


async def gen_token_pair_and_create_session(
    scopes: list[str], user_id: int, app_id: UUID, session: AsyncSession
) -> OAuth2CodeExchangeResponse:
    scopes_str = " ".join(scopes)
    refresh_token_bytes = gen_refresh_token_bytes()
    access_token, refresh_token = create_token_pair(
        payload=OAuth2AccessTokenPayload(sub=str(user_id), scopes=scopes),
        refresh_token_bytes=refresh_token_bytes,
    )
    await OAuth2SessionsDB.create_session(
        user_id=user_id,
        session_id=uuid4(),
        refresh_token_hash=hash_token(refresh_token_bytes),
        app_id=app_id,
        scope=scopes_str,
        session=session,
    )
    return OAuth2CodeExchangeResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        scope=scopes_str,
    )


async def update_session_and_gen_new_token(
    oauth2_session: OAuth2SessionsInDB, session: AsyncSession
) -> OAuth2CodeExchangeResponse:
    scopes = oauth2_session.scope.split(" ")
    refresh_token_bytes = gen_refresh_token_bytes()
    access_token, refresh_token = create_token_pair(
        payload=OAuth2AccessTokenPayload(
            sub=str(oauth2_session.user_id), scopes=scopes
        ),
        refresh_token_bytes=refresh_token_bytes,
    )
    await OAuth2SessionsDB.update(
        oauth2_session=oauth2_session,
        refresh_token_hash=hash_token(refresh_token_bytes),
        session=session,
    )
    return OAuth2CodeExchangeResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        scope=oauth2_session.scope,
    )
