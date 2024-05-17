from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.apps.service import AppsService
from src.auth.dependencies import UserAuthorization
from src.mongo import db

from .exceptions import AppNotFound, UnauthorizedAccess
from .repository import AppsRepository
from .schemas import AppInMongo

service = AppsService(
    repository=AppsRepository(
        collection=db["apps"],
    )
)


async def get_apps_service() -> AppsService:
    return service


AppsServiceDep = Annotated[AppsService, Depends(get_apps_service)]


async def get_existed_app(app_id: UUID, service: AppsServiceDep) -> AppInMongo:
    found_app = await service.get(app_id)
    if not found_app:
        raise AppNotFound()
    return found_app


ExistedApp = Annotated[AppInMongo, Depends(get_existed_app)]


async def valid_access_app(app: ExistedApp, user: UserAuthorization) -> AppInMongo:
    if app.creator_id != user.id:
        raise UnauthorizedAccess()
    return app


AppAccessControlDep = Annotated[AppInMongo, Depends(valid_access_app)]


async def existed_app_by_client_id(
    client_id: UUID,
    service: AppsServiceDep,
) -> AppInMongo:
    found_app = await service.get_by_client_id(client_id)
    if not found_app:
        raise AppNotFound()
    return found_app


ExistedAppByClientId = Annotated[AppInMongo, Depends(existed_app_by_client_id)]
