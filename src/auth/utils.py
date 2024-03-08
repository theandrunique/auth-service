import datetime
import secrets
import string
import uuid
from typing import Any

import bcrypt
import jwt
from jwt.exceptions import PyJWTError

from src.config import settings

from .schemas import (
    TokenType,
    UserAccessTokenPayload,
    UserRefreshTokenPayload,
    UserTokenPair,
)


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


def validate_token(token: str, token_type: TokenType) -> dict[str, Any]:
    payload_dict: dict[str, Any] = jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    if payload_dict.get("token_type") != token_type.value:
        raise PyJWTError()
    return payload_dict


def validate_access_token(token: str) -> UserAccessTokenPayload:
    payload = validate_token(token=token, token_type=TokenType.ACCESS)
    return UserAccessTokenPayload(**payload)


def validate_refresh_token(token: str) -> UserRefreshTokenPayload:
    payload = validate_token(token=token, token_type=TokenType.REFRESH)
    return UserRefreshTokenPayload(**payload)


def check_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


def create_tokens(
    refresh_payload: UserRefreshTokenPayload,
    access_payload: UserAccessTokenPayload,
) -> UserTokenPair:
    access_token = _create_token(
        data=access_payload.model_dump(),
        expires_delta=datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type=TokenType.ACCESS,
    )
    refresh_token = _create_token(
        data=refresh_payload.model_dump(),
        expires_delta=datetime.timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
        token_type=TokenType.REFRESH,
    )
    return UserTokenPair(
        refresh_token=refresh_token,
        access_token=access_token,
    )
