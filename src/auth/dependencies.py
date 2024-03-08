from typing import Annotated

from fastapi import Depends, Request
from jwt import PyJWTError
from pydantic import ValidationError

from src.database import DbSession
from src.models import UserInDB

from .crud import get_user_from_db_by_id
from .exceptions import InactiveUser, InvalidToken, NotAuthenticated, UserNotFound
from .utils import validate_access_token


async def get_authorization(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise NotAuthenticated()
    return authorization


async def get_user(
    session: DbSession,
    token: str = Depends(get_authorization),
) -> UserInDB:
    try:
        payload = validate_access_token(token=token)
    except (PyJWTError, ValidationError):
        raise InvalidToken()
    user = await get_user_from_db_by_id(id=payload.id, session=session)
    if user is None:
        raise UserNotFound()
    elif not user.active:
        raise InactiveUser()
    return user


UserAuthorization = Annotated[UserInDB, Depends(get_user)]
