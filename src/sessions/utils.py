from datetime import datetime

from fastapi import Response

from src.config import settings


def set_session_cookie(token: str, expire: datetime, res: Response):
    res.set_cookie(settings.SESSION_KEY, token, httponly=True, expires=expire)


def delete_session_cookie(res: Response):
    res.delete_cookie(settings.SESSION_KEY)
