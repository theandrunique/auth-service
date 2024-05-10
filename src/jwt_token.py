from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError

from src.config import settings
from src.utils import UUIDEncoder


def create(
    payload: dict[str, Any],
) -> str:
    payload["iss"] = settings.DOMAIN_URL
    encoded = jwt.encode(
        payload=payload,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        json_encoder=UUIDEncoder,
    )
    return encoded


def decode(token: str, audience: str | None = None) -> dict[str, Any] | None:
    try:
        return jwt.decode(  # type: ignore
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            issuer=settings.DOMAIN_URL,
            audience=audience,
        )
    except InvalidTokenError as e:
        print(e)
        return None
