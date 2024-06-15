from typing import Annotated

from fastapi import Security, params
from redis.asyncio import Redis

from src.apps.service import AppsService
from src.auth.exceptions import InvalidSession
from src.container import container
from src.oauth2.service import OAuth2Service
from src.oauth2_sessions.service import OAuth2SessionsService
from src.services.authoritative_apps import AuthoritativeAppsService
from src.services.base import hash, jwe, jwt
from src.sessions.dependencies import SessionCookie
from src.sessions.schemas import SessionSchema
from src.sessions.service import SessionsService
from src.users.exceptions import InactiveUser
from src.users.schemas import UserSchema
from src.users.service import UsersService
from src.well_known.service import WellKnownService


class Container:
    JWT = jwt.JWT
    JWE = jwe.JWE
    Hash = hash.Hash
    Redis = Redis

    SessionsService = SessionsService
    AppsService = AppsService
    OAuth2SessionsService = OAuth2SessionsService
    UsersService = UsersService
    WellKnownService = WellKnownService
    OAuth2Service = OAuth2Service
    AuthoritativeAppsService = AuthoritativeAppsService


def Provide[T](
    dependency: type[T],
) -> T:
    def _dependency():
        return container.resolve(dependency)

    return params.Depends(dependency=_dependency, use_cache=True)  # type: ignore


def resolve[T](dependency: type[T]) -> T:
    return container.resolve(dependency)  # type: ignore


async def get_user_with_session(
    session_cookie: SessionCookie,
    users_service=Provide(Container.UsersService),
    sessions_service=Provide(Container.SessionsService),
) -> tuple[UserSchema, SessionSchema]:
    session = await sessions_service.get(session_cookie.token)
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
