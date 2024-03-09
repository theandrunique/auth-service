from typing import Annotated

from fastapi import Request, Security
from jwt import PyJWTError
from pydantic import ValidationError

from src.database import DbSession
from src.models import UserInDB

from .crud import get_user_from_db_by_id, get_user_session_from_db
from .exceptions import InactiveUser, InvalidToken, NotAuthenticated, UserNotFound
from .utils import validate_user_token


async def get_authorization(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise NotAuthenticated()
    return authorization


async def get_user(
    session: DbSession,
    token: str = Security(get_authorization),
) -> UserInDB:
    try:
        payload = validate_user_token(token=token)
    except (PyJWTError, ValidationError):
        raise InvalidToken()
    user_session = await get_user_session_from_db(
        user_id=payload.user_id,
        session_id=payload.jti,
        session=session,
    )
    if user_session is None:
        raise InvalidToken()

    user = await get_user_from_db_by_id(id=payload.user_id, session=session)
    if user is None:
        raise UserNotFound()
    elif not user.active:
        raise InactiveUser()
    return user


UserAuthorization = Annotated[UserInDB, Security(get_user)]
