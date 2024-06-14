from typing import Any
from uuid import UUID

import httpx
from fastapi import APIRouter, Query

from src.dependencies import Container, Provide, UserAuthorization

from .exceptions import InvalidImageUrl, UserNotFound
from .schemas import SearchResult, UpdateImage, UserPublic

router = APIRouter(tags=["users"])


@router.get("", response_model=SearchResult)
async def get_users(
    users_service=Provide(Container.UsersService),
    user_ids: list[UUID] = Query(),
) -> Any:
    result = await users_service.get_many(user_ids)
    return SearchResult(
        result=result if result else [],
        total=len(result) if result else 0,
    )


@router.get("/me", response_model=UserPublic)
async def get_me(user: UserAuthorization) -> Any:
    return user


@router.get("/@{username}", response_model=UserPublic)
async def get_user_by_username(
    username: str, users_service=Provide(Container.UsersService)
) -> Any:
    user = await users_service.get_by_username(username)
    if not user:
        raise UserNotFound()
    return user


@router.get("/search", response_model=SearchResult)
async def search_users(
    query: str, users_service=Provide(Container.UsersService)
) -> Any:
    result = await users_service.search_by_username(query)
    return SearchResult(
        result=result if result else [],
        total=len(result) if result else 0,
    )


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: UUID, users_service=Provide(Container.UsersService)) -> Any:
    user = await users_service.get(user_id)
    if not user:
        raise UserNotFound()
    return user


@router.put("/me/image_url", response_model=UserPublic)
async def update_user_image_url(
    user: UserAuthorization,
    image: UpdateImage,
    users_service=Provide(Container.UsersService),
) -> Any:
    async with httpx.AsyncClient() as client:
        res = await client.get(str(image.image_url))
        if res.status_code != 200 or "image" not in res.headers["Content-Type"]:
            raise InvalidImageUrl()

    updated_user = await users_service.update(
        user.id, {"image_url": str(image.image_url)}
    )
    return updated_user
