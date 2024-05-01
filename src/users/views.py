from typing import Any

from fastapi import APIRouter

from src.auth.dependencies import UserAuthorization

from .schemas import UserPublic

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserPublic)
async def get_me(user: UserAuthorization) -> Any:
    return user
