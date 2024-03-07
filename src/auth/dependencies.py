from typing import Annotated

from fastapi import Depends, Request
from jwt import PyJWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_helper import db_helper
from src.models import UserInDB

from .crud import get_user_from_db_by_id
from .exceptions import InvalidToken, NotAuthenticated, UserNotFound
from .schemas import TokenType
from .security import validate_token


async def get_authorization(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise NotAuthenticated()
    return authorization


async def get_user(
    token: str = Depends(get_authorization),
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> UserInDB:
    try:
        payload = validate_token(token=token, token_type=TokenType.ACCESS)
    except (PyJWTError, ValidationError):
        raise InvalidToken()
    user = await get_user_from_db_by_id(id=payload.sub, session=session)
    if user is None:
        raise UserNotFound()
    return user


UserAuthorization = Annotated[UserInDB, Depends(get_user)]
