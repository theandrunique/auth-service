from datetime import UTC, datetime, timedelta

from fastapi import Response

from src.config import settings


def set_session_cookie(token: str, res: Response):
    res.set_cookie(
        settings.SESSION_KEY,
        token,
        httponly=True,
        expires=datetime.now(UTC) + timedelta(hours=settings.SESSION_EXPIRE_HOURS),
    )


def delete_session_cookie(res: Response):
    res.delete_cookie(settings.SESSION_KEY)
