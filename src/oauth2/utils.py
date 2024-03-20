import base64
import hashlib
import secrets
from uuid import UUID, uuid4

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings

from .crud import create_oauth2_session
from .schemas import OAuth2AccessTokenPayload, OAuth2CodeExchangeResponse

REFRESH_TOKEN_LENGTH = 64


def gen_authorization_code() -> str:
    return uuid4().hex


def align_b64(b64_string):
    missing = len(b64_string) % 4
    return f"{b64_string}{'=' * missing}"


def validate_token(token: str, token_hash: bytes):
    b64_decoded = base64.urlsafe_b64decode(align_b64(token))
    input_hash = hashlib.sha256(b64_decoded)
    return secrets.compare_digest(input_hash.digest(), token_hash)


def gen_access_token(payload: OAuth2AccessTokenPayload) -> str:
    return jwt.encode(
        payload=payload.model_dump(),
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def gen_refresh_token_bytes() -> bytes:
    return secrets.token_bytes(REFRESH_TOKEN_LENGTH)


def get_token_from_bytes(token_bytes: bytes) -> str:
    return base64.urlsafe_b64encode(token_bytes).rstrip(b"=").decode("utf-8")


def hash_token(token_bytes: bytes) -> bytes:
    return hashlib.sha256(token_bytes).digest()


async def gen_token_pair_and_create_session(
    scope: str, user_id: int, app_id: UUID, session: AsyncSession
):
    refresh_token_bytes = gen_refresh_token_bytes()
    refresh_token = get_token_from_bytes(refresh_token_bytes)
    access_token = gen_access_token(
        OAuth2AccessTokenPayload(
            sub=str(user_id),
            scope=scope,
        )
    )
    await create_oauth2_session(
        user_id=user_id,
        session_id=uuid4(),
        refresh_token_hash=hash_token(refresh_token_bytes),
        app_id=app_id,
        scope=scope,
        session=session,
    )
    return OAuth2CodeExchangeResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=3600,
        scope=scope,
    )
