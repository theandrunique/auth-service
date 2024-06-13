from fastapi import APIRouter, status

from src.auth.dependencies import UserAuthorization
from src.dependencies import Container, Provide

from .dependencies import AppAccessControlDep, ExistedApp
from .schemas import (
    AppCreate,
    AppCreateSchema,
    AppInMongo,
    AppPublicSchema,
    AppUpdateSchema,
)

router = APIRouter(prefix="", tags=["apps"])


@router.put(
    "/{app_id}/client-secret",
    response_model=AppInMongo,
)
async def regenerate_client_secret(
    app: AppAccessControlDep,
    apps_service=Provide(Container.AppsService),
) -> AppInMongo:
    return await apps_service.regenerate_client_secret(app.id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_app(
    app: AppCreateSchema,
    user: UserAuthorization,
    apps_service=Provide(Container.AppsService),
) -> AppInMongo:
    new_app_data = AppCreate(**app.model_dump(), creator_id=user.id)
    new_app = await apps_service.add(new_app_data)
    return new_app


@router.get("/{app_id}")
async def get_app_by_id(
    app: ExistedApp,
    user: UserAuthorization,
) -> AppInMongo | AppPublicSchema:
    if user and app.creator_id == user.id:
        return app
    return AppPublicSchema(**app.model_dump())


@router.patch("/{app_id}")
async def update_app(
    app: AppAccessControlDep,
    data: AppUpdateSchema,
    apps_service=Provide(Container.AppsService),
) -> AppInMongo:
    new_values = data.model_dump(exclude_defaults=True)
    if new_values:
        return await apps_service.update(app.id, new_values)
    else:
        return app


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app(
    app: AppAccessControlDep,
    apps_service=Provide(Container.AppsService),
) -> None:
    await apps_service.delete(app.id)
