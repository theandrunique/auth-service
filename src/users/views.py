from typing import Any

from fastapi import APIRouter

from src.auth.dependencies import UserAuthorization
from src.users.schemas import UserSchema

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSchema)
async def get_me(user: UserAuthorization) -> Any:
    return user
