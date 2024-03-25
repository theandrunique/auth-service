from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, status

from src.auth.dependencies import UserAuthorization, UserAuthorizationOptional

from .exceptions import AppNotFound, UnauthorizedAccess
from .registry import AppsRegistry
from .schemas import (
    AppCreate,
    AppInMongo,
    AppPublicSchema,
    AppUpdate,
)

router = APIRouter(prefix="", tags=["apps"])


@router.put(
    "/{app_id}/regenerate-client-secret/",
    response_model=AppInMongo,
    response_model_by_alias=False,
)
async def regenerate_client_secret(app_id: UUID, user: UserAuthorization) -> Any:
    app = await AppsRegistry.get(app_id)
    if app is None:
        raise AppNotFound()
    if app.creator_id != user.id:
        raise UnauthorizedAccess()
    app.client_secret = uuid4()
    await AppsRegistry.update(app_id, {"client_secret": app.client_secret})
    return app


@router.post("/", status_code=status.HTTP_201_CREATED, response_model_by_alias=False)
async def create_app(app: AppCreate, user: UserAuthorization) -> Any:
    new_app = AppInMongo(**app.model_dump(), creator_id=user.id)
    await AppsRegistry.add(new_app)
    return new_app


@router.get("/{app_id}/", response_model_by_alias=False)
async def get_app_by_id(
    app_id: UUID, user: UserAuthorizationOptional
) -> AppInMongo | AppPublicSchema:
    app = await AppsRegistry.get(app_id)
    if app is None:
        raise AppNotFound()
    if user and app.creator_id == user.id:
        return app
    return AppPublicSchema(**app.model_dump())


@router.patch("/{app_id}/", response_model_by_alias=False)
async def update_app(
    app_id: UUID, data: AppUpdate, user: UserAuthorization
) -> AppInMongo:
    new_values = data.model_dump(exclude_defaults=True)

    app = await AppsRegistry.get(app_id)
    if app is None:
        raise AppNotFound()

    if app.creator_id != user.id:
        raise UnauthorizedAccess()

    if new_values:
        return await AppsRegistry.update(app_id, new_values)
    else:
        return app


@router.delete("/{app_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app(app_id: UUID, user: UserAuthorization) -> None:
    app = await AppsRegistry.get(app_id)
    if app is None:
        raise AppNotFound()

    if app.creator_id != user.id:
        raise UnauthorizedAccess()

    await AppsRegistry.delete(app_id)
