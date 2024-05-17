from typing import Annotated
from uuid import UUID

from fastapi import Cookie, Depends

from src.auth.exceptions import NotAuthenticated
from src.mongo import db

from .config import settings
from .repository import SessionsRepository
from .schemas import SessionCookies
from .service import SessionsService

service = SessionsService(repository=SessionsRepository(collection=db["session"]))


def get_user_sessions_service() -> SessionsService:
    return service


SessionServiceDep = Annotated[SessionsService, Depends(get_user_sessions_service)]


def get_user_session_cookies(
    session_key: UUID | None = Cookie(
        alias=settings.ID_KEY, default=None, include_in_schema=False
    ),
    session_token: str | None = Cookie(
        alias=settings.VALUE_KEY, default=None, include_in_schema=False
    ),
) -> SessionCookies:
    if not session_key or not session_token:
        raise NotAuthenticated()
    return SessionCookies(key=session_key, token=session_token)


UserSession = Annotated[SessionCookies, Depends(get_user_session_cookies)]
