from pydantic import ValidationError

from src import jwt_token

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
