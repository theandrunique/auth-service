from typing import Any

from fastapi import APIRouter
from pydantic import PositiveInt

from src.dependencies import DbSession, UserAuthorization

from .crud import UsersDB
from .exceptions import UserNotFound
from .schemas import UserSchema

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserSchema)
async def get_me(user: UserAuthorization) -> Any:
    return user


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: PositiveInt, session: DbSession) -> Any:
    found_user = await UsersDB.get_by_id(id=user_id, session=session)
    if not found_user:
        raise UserNotFound()
    return found_user

