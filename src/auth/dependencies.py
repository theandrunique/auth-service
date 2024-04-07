from typing import Annotated

import jwt
from fastapi import Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import UserTokenPayload
from src.config import settings
from src.dependencies import DbSession
from src.oauth2.schemas import OAuth2AccessTokenPayload
from src.sessions.crud import SessionsDB
from src.sessions.models import UserSessionsInDB
from src.users.crud import UsersDB
from src.users.exceptions import (
    InactiveUser,
    UserNotFound,
)
from src.users.models import UserInDB

from .exceptions import (
    InvalidToken,
    MissingScope,
    NotAuthenticated,
    NotSupportedByOAuth2,
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/oauth2/token/",
    auto_error=False,
)


BearerToken = Annotated[str | None, Security(oauth2_scheme)]


def decode_payload(
    token: str,
) -> UserTokenPayload | OAuth2AccessTokenPayload:
    try:
        payload_dict = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if "scopes" in payload_dict:
            return OAuth2AccessTokenPayload(**payload_dict)
        else:
            return UserTokenPayload(**payload_dict)
    except ExpiredSignatureError:
        raise InvalidToken()
    except (PyJWTError, ValidationError):
        raise InvalidToken()


def get_authorization(token: BearerToken) -> str:
    if not token:
        raise NotAuthenticated()
    return token


def get_authorization_optional(token: BearerToken) -> str | None:
    return token


async def authenticate_as_user(
    payload: UserTokenPayload, session: AsyncSession
) -> tuple[UserInDB, UserSessionsInDB]:
    user, user_session = await UsersDB.get_with_session(
        user_id=payload.sub,
        session_id=payload.jti,
        session=session,
    )
    if user is None:
        raise UserNotFound()
    if user_session is None:
        raise InvalidToken()
    elif not user.active:
        raise InactiveUser()
    await SessionsDB.update_last_used(user_session=user_session, session=session)
    return user, user_session


async def authenticate_as_oauth2(
    req_scopes: SecurityScopes, payload: OAuth2AccessTokenPayload, session: AsyncSession
) -> UserInDB:
    disallowed_scopes = [
        scope for scope in payload.scopes if scope not in req_scopes.scopes
    ]
    if disallowed_scopes:
        raise MissingScope(disallowed_scopes)
    user = await UsersDB.get_by_id(id=int(payload.sub), session=session)
    if user is None:
        raise UserNotFound()
    return user


async def user_authorization(
    req_scopes: SecurityScopes,
    session: DbSession,
    token: str = Security(get_authorization),
) -> tuple[UserInDB, UserSessionsInDB | None]:
    payload = decode_payload(token)
    if isinstance(payload, UserTokenPayload):
        return await authenticate_as_user(payload, session)
    elif isinstance(payload, OAuth2AccessTokenPayload):
        user = await authenticate_as_oauth2(req_scopes, payload, session)
        return user, None


UserAuthorizationDep = Annotated[
    tuple[UserInDB, UserSessionsInDB | None], Security(user_authorization)
]


async def get_user(
    user_with_session: UserAuthorizationDep,
) -> UserInDB:
    user, _ = user_with_session
    return user


async def get_user_with_session(
    user_with_session: UserAuthorizationDep,
) -> tuple[UserInDB, UserSessionsInDB]:
    """
    Get user with session.

    Returns tuple with user session and user.

    Raises:
        NotSupportedByOAuth2: If session is None - its OAuth2 token
            and it does not support sessions
    """
    user, user_session = user_with_session
    if user_session is None:
        raise NotSupportedByOAuth2()
    return user, user_session


async def get_user_optional(
    req_scopes: SecurityScopes,
    session: DbSession,
    token: str | None = Security(get_authorization_optional),
) -> UserInDB | None:
    if token is None:
        return None
    else:
        user, _ = await user_authorization(
            req_scopes=req_scopes, token=token, session=session
        )
        return user
