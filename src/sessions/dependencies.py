from typing import Annotated

from fastapi import Cookie, Depends

from src.auth.exceptions import NotAuthenticated
from src.config import settings

from .schemas import SessionCookies


def get_user_session_cookies(
    session_token: str | None = Cookie(
        alias=settings.SESSION_KEY, default=None, include_in_schema=False
    ),
) -> SessionCookies:
    if not session_token:
        raise NotAuthenticated()
    return SessionCookies(token=session_token)


SessionCookie = Annotated[SessionCookies, Depends(get_user_session_cookies)]
