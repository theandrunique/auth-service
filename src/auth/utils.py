import datetime
import secrets
import string
import uuid
from typing import Any

import bcrypt
import jwt

from src.config import settings

from .schemas import (
    UserTokenPayload,
    UserTokenSchema,
)


def gen_otp() -> str:
    return "".join(secrets.choice(string.digits) for _ in range(6))


def gen_random_token_id() -> uuid.UUID:
    return uuid.uuid4()


def _create_token(
    data: dict[str, Any],
    expires_delta: datetime.timedelta,
) -> str:
    encoded_jwt = jwt.encode(
        payload={
            **data,
            "exp": datetime.datetime.now(datetime.timezone.utc) + expires_delta,
        },
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def validate_user_token(token: str) -> UserTokenPayload:
    payload = jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    return UserTokenPayload(**payload)


def check_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


def create_user_token(
    payload: UserTokenPayload,
) -> UserTokenSchema:
    token = _create_token(
        data=payload.model_dump(),
        expires_delta=datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return UserTokenSchema(
        user_id=payload.user_id,
        token=token,
    )
