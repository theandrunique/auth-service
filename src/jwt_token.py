from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError

from src.config import settings
from src.utils import UUIDEncoder


def create(
    payload: dict[str, Any],
) -> str:
    encoded = jwt.encode(
        payload=payload,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        json_encoder=UUIDEncoder,
    )
    return encoded


def decode(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(  # type: ignore
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except InvalidTokenError:
        return None
