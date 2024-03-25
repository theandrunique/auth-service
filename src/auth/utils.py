import datetime
import secrets
import string
import uuid
from typing import Any

import bcrypt
import jwt
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.crud import SessionsDB
from src.config import settings
from src.models import UserInDB

from .schemas import (
    UserTokenPayload,
    UserTokenSchema,
)


def gen_otp_with_token() -> tuple[str, str]:
    otp = "".join(secrets.choice(string.digits) for _ in range(6))
    token = secrets.token_urlsafe(40)
    return otp, token


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


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(
        password=password.encode(),
        salt=bcrypt.gensalt(),
    )


def create_user_token(
    payload: UserTokenPayload,
) -> UserTokenSchema:
    token = _create_token(
        data=payload.model_dump(),
        expires_delta=datetime.timedelta(hours=settings.USER_TOKEN_EXPIRE_HOURS),
    )
    return UserTokenSchema(
        user_id=payload.user_id,
        token=token,
    )


async def create_new_session(
    req: Request,
    user: UserInDB,
    session: AsyncSession,
) -> str:
    jti = uuid.uuid4()
    await SessionsDB.create_new(
        user_id=user.id,
        session_id=jti,
        ip_address=req.client.host if req.client else None,
        session=session,
    )
    return create_user_token(
        payload=UserTokenPayload(user_id=user.id, email=user.email, jti=jti.hex)
    )
