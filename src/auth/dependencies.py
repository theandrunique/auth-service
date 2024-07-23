from typing import Annotated

from fastapi import Response, Security

from src.auth.exceptions import InvalidSession, NotAuthenticated
from src.auth.service import IAuthService
from src.dependencies import Provide
from src.sessions.dependencies import SessionCookie
from src.sessions.entities import Session
from src.sessions.utils import delete_session_cookie
from src.users.entities import User


async def validate_session(
    session_cookie: SessionCookie, res: Response, auth_service=Provide(IAuthService)
) -> tuple[User, Session] | None:
    if session_cookie is None:
        return None
    try:
        return await auth_service.validate_session(session_cookie.token)
    except InvalidSession as e:
        delete_session_cookie(res=res)
        raise e


async def get_user_with_session(
    session: Annotated[tuple[User, Session] | None, Security(validate_session)],
) -> tuple[User, Session]:
    if session is None:
        raise NotAuthenticated

    return session


UserAuthorizationWithSession = Annotated[tuple[User, Session], Security(get_user_with_session)]


async def get_user(
    user_with_session: UserAuthorizationWithSession,
) -> User:
    user, _ = user_with_session
    return user


UserAuthorization = Annotated[User, Security(get_user)]


async def get_user_with_session_optional(
    session: Annotated[tuple[User, Session] | None, Security(validate_session)],
) -> tuple[User, Session] | None:
    if session is None:
        return None
    else:
        return session


UserAuthorizationWithSessionOptional = Annotated[tuple[User, Session] | None, Security(get_user_with_session_optional)]


async def get_user_optional(
    session: Annotated[tuple[User, Session] | None, Security(validate_session)],
) -> User | None:
    if session is None:
        return None
    else:
        return session[0]


UserAuthorizationOptional = Annotated[User | None, Security(get_user_optional)]
