import datetime
import secrets
import string
import uuid
from typing import Any

import bcrypt
import jwt
from config import settings
from jwt.exceptions import PyJWTError

from .schemas import TokenPair, TokenPayload, TokenType


def gen_key() -> str:
    return secrets.token_urlsafe(settings.KEYS_LENGTH)


def gen_otp() -> str:
    return "".join(secrets.choice(string.digits) for _ in range(6))


def gen_random_token_id() -> str:
    return uuid.uuid4().hex


def _create_token(
    data: dict[str, Any],
    expires_delta: datetime.timedelta,
    token_type: TokenType,
) -> str:
    encoded_jwt = jwt.encode(
        payload={
            **data,
            "exp": datetime.datetime.now(datetime.timezone.utc) + expires_delta,
            "token_type": token_type.value,
        },
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def validate_token(token: str, token_type: TokenType) -> TokenPayload:
    payload_dict: dict[str, Any] = jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    payload = TokenPayload(**payload_dict)
    if payload_dict["token_type"] != token_type.value:
        raise PyJWTError()
    return payload


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(
        password=password.encode(),
        salt=bcrypt.gensalt(),
    )


def create_tokens(payload: TokenPayload) -> TokenPair:
    payload_dict = payload.model_dump()
    access_token = _create_token(
        data=payload_dict,
        expires_delta=datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type=TokenType.ACCESS,
    )
    refresh_token = _create_token(
        data=payload_dict,
        expires_delta=datetime.timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
        token_type=TokenType.REFRESH,
    )
    return TokenPair(
        refresh_token=refresh_token,
        access_token=access_token,
        scope=payload.scopes,
    )
