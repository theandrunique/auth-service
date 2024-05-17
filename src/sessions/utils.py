from datetime import datetime
from secrets import token_urlsafe

from fastapi import Response

from .config import settings


def gen_session_token() -> str:
    return token_urlsafe(settings.TOKEN_BYTES_LENGTH)


def set_session(key: str, token: str, expire: datetime, res: Response):
    res.set_cookie(settings.ID_KEY, key, httponly=True, expires=expire)
    res.set_cookie(settings.VALUE_KEY, token, httponly=True, expires=expire)
