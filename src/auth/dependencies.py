from typing import Annotated

from fastapi import Security
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from pydantic import ValidationError

from src.auth.models import UserSessionsInDB
from src.auth.sessions.crud import SessionsDB
from src.database import DbSession
from src.models import UserInDB

from .crud import UsersDB
from .exceptions import InactiveUser, InvalidToken, NotAuthenticated, UserNotFound
from .utils import validate_user_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/oauth2/token/",
    auto_error=False,
)


async def get_authorization_optional(
    token: str = Security(oauth2_scheme),
) -> str | None:
    return token


async def get_authorization(token: str = Security(oauth2_scheme)) -> str:
    if not token:
        raise NotAuthenticated()
    return token


async def get_user_with_session(
    session: DbSession,
    token: str = Security(get_authorization),
) -> tuple[UserInDB, UserSessionsInDB]:
    try:
        payload = validate_user_token(token=token)
    except ExpiredSignatureError:
        raise InvalidToken()
    except (PyJWTError, ValidationError):
        raise InvalidToken()
    user, user_session = await UsersDB.get_with_session(
        user_id=payload.user_id,
        session_id=payload.jti,
        session=session,
    )
    if user_session is None:
        raise InvalidToken()
    if user is None:
        raise UserNotFound()
    elif not user.active:
        raise InactiveUser()
    await SessionsDB.update_last_used(user_session=user_session, session=session)
    return user, user_session


UserAuthorizationWithSession = Annotated[
    tuple[UserInDB, UserSessionsInDB], Security(get_user_with_session)
]


async def get_user(
    user_and_session: UserAuthorizationWithSession,
) -> UserInDB:
    user, _ = user_and_session
    return user


UserAuthorization = Annotated[UserInDB, Security(get_user)]


async def get_user_authorization_optional(
    session: DbSession,
    token: str | None = Security(get_authorization_optional),
) -> UserInDB | None:
    if token is None:
        return None
    else:
        user, _ = await get_user_with_session(session=session, token=token)
        return user


UserAuthorizationOptional = Annotated[
    UserInDB | None, Security(get_user_authorization_optional)
]
