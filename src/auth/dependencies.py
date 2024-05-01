from typing import Annotated

from fastapi import Security
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError
from pydantic import ValidationError

from src.mongo.dependencies import MongoSession
from src.sessions.repository import SessionsRepository
from src.sessions.schemas import SessionSchema
from src.users.dependencies import UsersRepositoryDep
from src.users.exceptions import (
    InactiveUser,
)
from src.users.schemas import UserSchema

from .exceptions import (
    InvalidToken,
    NotAuthenticated,
)
from .utils import decode_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="",
    auto_error=False,
)


BearerToken = Annotated[str | None, Security(oauth2_scheme)]


def get_authorization(token: BearerToken) -> str:
    if not token:
        raise NotAuthenticated()
    return token


def get_authorization_optional(token: BearerToken) -> str | None:
    return token


async def get_user_with_session(
    mongo_session: MongoSession,
    users_repository: UsersRepositoryDep,
    token: str = Security(get_authorization),
) -> tuple[UserSchema, SessionSchema]:
    try:
        payload = decode_token(token=token)
    except (PyJWTError, ValidationError):
        raise InvalidToken()

    user = await users_repository.get(id=payload.sub)
    if user is None:
        raise InvalidToken()
    elif not user.active:
        raise InactiveUser()

    sessions_repository = SessionsRepository(session=mongo_session, user_id=user.id)

    session = await sessions_repository.get(id=payload.jti)
    if session is None:
        raise InvalidToken()

    await sessions_repository.update_last_used(id=session.id)
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


async def get_user_optional(
    mongo_session: MongoSession,
    users_repository: UsersRepositoryDep,
    token: str | None = Security(get_authorization_optional),
) -> UserSchema | None:
    if token is None:
        return None
    else:
        user, _ = await get_user_with_session(
            mongo_session=mongo_session,
            users_repository=users_repository,
            token=token,
        )
        return user


UserAuthorizationOptional = Annotated[
    UserSchema | None,
    Security(get_user_optional),
]
