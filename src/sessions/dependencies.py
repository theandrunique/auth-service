from typing import Annotated

from fastapi import Cookie, Depends

from src.config import settings

from .schemas import SessionCookies


def get_user_session_cookies(
    session_token: str | None = Cookie(alias=settings.SESSION_KEY, default=None, include_in_schema=False),
) -> SessionCookies | None:
    if not session_token:
        return None

    return SessionCookies(token=session_token)


SessionCookie = Annotated[SessionCookies | None, Depends(get_user_session_cookies)]
