import secrets
import string
import uuid
from typing import Any

import bcrypt
import jwt
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models import UserInDB
from src.sessions.crud import SessionsDB
from src.utils import UUIDEncoder

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
) -> str:
    encoded_jwt = jwt.encode(
        payload={
            **data,
        },
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        json_encoder=UUIDEncoder,
    )
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(  # type: ignore
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )


def validate_user_token(token: str) -> UserTokenPayload:
    payload = decode_token(token=token)
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
    )
    return UserTokenSchema(
        user_id=payload.sub,
        token=token,
    )


async def create_new_session(
    req: Request,
    user: UserInDB,
    session: AsyncSession,
) -> UserTokenSchema:
    jti = uuid.uuid4()
    await SessionsDB.create_new(
        user_id=user.id,
        session_id=jti,
        ip_address=req.client.host if req.client else None,
        session=session,
    )
    return create_user_token(
        payload=UserTokenPayload(sub=user.id, jti=jti)
    )
