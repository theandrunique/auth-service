from typing import Any
from uuid import uuid4

from fastapi import APIRouter, status

from src.dependencies import UserAuthorization, UserAuthorizationOptional

from .dependencies import AppAccessControlDep, AppDep
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
async def regenerate_client_secret(app: AppAccessControlDep) -> Any:
    app.client_secret = uuid4()
    await AppsRegistry.update(app.id, {"client_secret": app.client_secret})
    return app


@router.post("/", status_code=status.HTTP_201_CREATED, response_model_by_alias=False)
async def create_app(app: AppCreate, user: UserAuthorization) -> Any:
    new_app = AppInMongo(**app.model_dump(), creator_id=user.id)
    await AppsRegistry.add(new_app)
    return new_app


@router.get("/{app_id}/", response_model_by_alias=False)
async def get_app_by_id(
    app: AppDep, user: UserAuthorizationOptional
) -> AppInMongo | AppPublicSchema:
    if user and app.creator_id == user.id:
        return app
    return AppPublicSchema(**app.model_dump())


@router.patch("/{app_id}/", response_model_by_alias=False)
async def update_app(
    app: AppAccessControlDep, data: AppUpdate,
) -> AppInMongo:
    new_values = data.model_dump(exclude_defaults=True)
    if new_values:
        return await AppsRegistry.update(app.id, new_values)
    else:
        return app


@router.delete("/{app_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app(app: AppAccessControlDep) -> None:
    await AppsRegistry.delete(app.id)
