import uuid
from typing import Any

import bcrypt
import jwt
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.sessions.crud import SessionsDB
from src.users.models import UserInDB
from src.utils import UUIDEncoder

from .schemas import (
    Token,
    TokenPayload,
)


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


def decode_token(token: str) -> TokenPayload:
    payload = jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    return TokenPayload(**payload)


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
    payload: TokenPayload,
) -> Token:
    token = _create_token(
        data=payload.model_dump(),
    )
    return Token(
        user_id=payload.sub,
        token=token,
    )


async def create_new_session(
    req: Request,
    user: UserInDB,
    session: AsyncSession,
) -> Token:
    jti = uuid.uuid4()
    await SessionsDB.create_new(
        user_id=user.id,
        session_id=jti,
        ip_address=req.client.host if req.client else None,
        session=session,
    )
    return create_user_token(payload=TokenPayload(sub=user.id, jti=jti))
