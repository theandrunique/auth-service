from typing import Annotated

from fastapi import Security

from src.dependencies import Container, Provide
from src.sessions.dependencies import UserSession
from src.sessions.schemas import SessionSchema
from src.users.exceptions import (
    InactiveUser,
)
from src.users.schemas import UserSchema

from .exceptions import InvalidSession


async def get_user_with_session(
    session_cookies: UserSession,
    users_service=Provide(Container.UsersService),
    sessions_service=Provide(Container.SessionsService),
) -> tuple[UserSchema, SessionSchema]:
    session = await sessions_service.get(session_cookies.token)
    if not session:
        raise InvalidSession()

    user = await users_service.get(id=session.user_id)
    if user is None:
        raise InvalidSession()
    elif not user.active:
        raise InactiveUser()

    await sessions_service.update_last_used(id=session.id)
    return user, session


UserAuthorizationWithSession = Annotated[
    tuple[UserSchema, SessionSchema], Security(get_user_with_session)
]


async def get_user(
    user_with_session: UserAuthorizationWithSession,
) -> UserSchema:
    user, _ = user_with_session
    return user


UserAuthorization = Annotated[UserSchema, Security(get_user)]
