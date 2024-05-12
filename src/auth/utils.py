from uuid import UUID

from fastapi import Request
from pydantic import ValidationError

from src import jwt_token
from src.sessions.schemas import SessionCreate
from src.sessions.service import sessions_service_factory

from .schemas import (
    Token,
    TokenPayload,
)


def decode_token(token: str) -> TokenPayload | None:
    payload = jwt_token.decode(token)
    if not payload:
        return None

    try:
        return TokenPayload(**payload)
    except ValidationError:
        return None


def create_token(
    payload: TokenPayload,
) -> Token:
    token = jwt_token.create(payload=payload.model_dump())
    return Token(
        user_id=payload.sub,
        token=token,
    )


async def create_session(user_id: UUID, req: Request) -> Token:
    service = sessions_service_factory(user_id)

    new_session = await service.add(
        SessionCreate(ip_address=req.client.host if req.client else None)
    )
    return create_token(payload=TokenPayload(sub=user_id, jti=new_session.id))
