from typing import Any
from uuid import uuid4

from fastapi import APIRouter, status

from src.dependencies import UserAuthorization, UserAuthorizationOptional

from .dependencies import AppAccessControlDep, AppDep, AppsRepositoryDep
from .schemas import (
    AppCreate,
    AppInMongo,
    AppPublic,
    AppUpdate,
)

router = APIRouter(prefix="", tags=["apps"])


@router.put(
    "/{app_id}/regenerate-client-secret/",
    response_model=AppInMongo,
    response_model_by_alias=False,
)
async def regenerate_client_secret(
    app: AppAccessControlDep,
    repository: AppsRepositoryDep,
) -> Any:
    app.client_secret = uuid4()
    await repository.update(app.id, {"client_secret": app.client_secret})
    return app


@router.post("/", status_code=status.HTTP_201_CREATED, response_model_by_alias=False)
async def create_app(
    app: AppCreate,
    user: UserAuthorization,
    repository: AppsRepositoryDep,
) -> Any:
    new_app = AppInMongo(**app.model_dump(), creator_id=user.id)
    await repository.add(new_app)
    return new_app


@router.get("/{app_id}/", response_model_by_alias=False)
async def get_app_by_id(
    app: AppDep,
    user: UserAuthorizationOptional,
    repository: AppsRepositoryDep,
) -> AppInMongo | AppPublic:
    if user and app.creator_id == user.id:
        return app
    return AppPublic(**app.model_dump())


@router.patch("/{app_id}/", response_model_by_alias=False)
async def update_app(
    app: AppAccessControlDep,
    data: AppUpdate,
    repository: AppsRepositoryDep,
) -> AppInMongo:
    new_values = data.model_dump(exclude_defaults=True)
    if new_values:
        return await repository.update(app.id, new_values)
    else:
        return app


@router.delete("/{app_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app(
    app: AppAccessControlDep,
    repository: AppsRepositoryDep,
) -> None:
    await repository.delete(app.id)
