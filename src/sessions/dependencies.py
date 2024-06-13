from typing import Annotated

from fastapi import Cookie, Depends

from src.auth.exceptions import NotAuthenticated

from .config import settings
from .schemas import SessionCookies


def get_user_session_cookies(
    session_token: str | None = Cookie(
        alias=settings.VALUE_KEY, default=None, include_in_schema=False
    ),
) -> SessionCookies:
    if not session_token:
        raise NotAuthenticated()
    return SessionCookies(token=session_token)


UserSession = Annotated[SessionCookies, Depends(get_user_session_cookies)]
