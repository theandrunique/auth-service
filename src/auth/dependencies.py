from typing import Annotated

from fastapi import Security
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import DbSession
from src.sessions.crud import SessionsDB
from src.sessions.models import UserSessionsInDB
from src.users.crud import UsersDB
from src.users.exceptions import (
    InactiveUser,
)
from src.users.models import UserInDB

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
    session: AsyncSession,
    token: str = Security(get_authorization),
) -> tuple[UserInDB, UserSessionsInDB]:
    try:
        payload = decode_token(token=token)
    except (PyJWTError, ValidationError):
        raise InvalidToken()
    user, user_session = await UsersDB.get_with_session(
        user_id=payload.sub,
        session_id=payload.jti,
        session=session,
    )
    if user is None:
        raise InvalidToken()
    if user_session is None:
        raise InvalidToken()
    elif not user.active:
        raise InactiveUser()
    await SessionsDB.update_last_used(user_session=user_session, session=session)
    return user, user_session


UserAuthorizationWithSession = Annotated[
    tuple[UserInDB, UserSessionsInDB], Security(get_user_with_session)
]


async def get_user(
    user_with_session: UserAuthorizationWithSession,
) -> UserInDB:
    user, _ = user_with_session
    return user


UserAuthorization = Annotated[UserInDB, Security(get_user)]


async def get_user_optional(
    session: DbSession,
    token: str | None = Security(get_authorization_optional),
) -> UserInDB | None:
    if token is None:
        return None
    else:
        user, _ = await get_user_with_session(token=token, session=session)
        return user


UserAuthorizationOptional = Annotated[
    tuple[UserInDB | None],
    Security(get_user_optional),
]
