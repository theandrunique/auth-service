from typing import Any
from uuid import UUID

import jwt
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClientSession

from src.config import settings
from src.sessions.repository import SessionsRepository
from src.sessions.schemas import SessionCreate
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


def create_token(
    payload: TokenPayload,
) -> Token:
    token = _create_token(
        data=payload.model_dump(),
    )
    return Token(
        user_id=payload.sub,
        token=token,
    )


async def create_session(
    session: AsyncIOMotorClientSession, user_id: UUID, req: Request
) -> Token:
    sessions_repository = SessionsRepository(session=session, user_id=user_id)

    new_session = await sessions_repository.add(
        SessionCreate(ip_address=req.client.host if req.client else None)
    )
    return create_token(payload=TokenPayload(sub=user_id, jti=new_session.id))
