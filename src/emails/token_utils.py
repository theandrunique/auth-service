from typing import Any

import jwt
from pydantic import ValidationError

from src.config import settings

from .schemas import EmailTokenPayload


def gen_email_token(
    payload: EmailTokenPayload,
) -> str:
    encoded_jwt = jwt.encode(
        payload=payload.model_dump(),
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def check_email_token(token: str) -> EmailTokenPayload | None:
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return EmailTokenPayload(**payload)
    except (jwt.exceptions.PyJWTError, ValidationError):
        return None
