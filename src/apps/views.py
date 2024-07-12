from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from src.apps.use_cases import (
    CreateAppCommand,
    CreateAppUseCase,
    GetUserAppsCommand,
    GetUserAppsUseCase,
    RegenerateClientSecretCommand,
    RegenerateClientSecretUseCase,
    UpdateAppInfoCommand,
    UpdateAppInfoUseCase,
)
from src.auth.dependencies import UserAuthorization
from src.dependencies import Provide

from .schemas import (
    AppCreateSchema,
    ApplicationSchema,
    AppUpdateSchema,
)

router = APIRouter(prefix="/oauth/applications", tags=["apps"])


@router.get("", response_model=list[ApplicationSchema])
async def get_apps(
    user: UserAuthorization,
    use_case=Provide(GetUserAppsUseCase),
) -> Any:
    return await use_case.execute(GetUserAppsCommand(user=user))


@router.put(
    "/{app_id}/client-secret",
    response_model=ApplicationSchema,
)
async def regenerate_client_secret(
    user: UserAuthorization,
    app_id: UUID,
    use_case=Provide(RegenerateClientSecretUseCase),
) -> Any:
    return await use_case.execute(RegenerateClientSecretCommand(user=user, app_id=app_id))


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ApplicationSchema)
async def create_app(
    data: AppCreateSchema,
    user: UserAuthorization,
    use_case=Provide(CreateAppUseCase),
) -> Any:
    return await use_case.execute(
        CreateAppCommand(
            user=user,
            name=data.name,
            redirect_uris=data.redirect_uris,
            scopes=data.scopes,
            description=data.description,
            website=data.website,
        )
    )


@router.patch("/{app_id}", response_model=ApplicationSchema)
async def update_app(
    user: UserAuthorization,
    app_id: UUID,
    data: AppUpdateSchema,
    use_case=Provide(UpdateAppInfoUseCase),
) -> Any:
    return await use_case.execute(
        UpdateAppInfoCommand(
            user=user,
            app_id=app_id,
            name=data.name,
            description=data.description,
            redirect_uris=data.redirect_uris,
            scopes=data.scopes,
        )
    )
