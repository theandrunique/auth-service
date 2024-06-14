from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.dependencies import Container, Provide, UserAuthorization
from src.schemas import PyObjectId

from .exceptions import AppNotFound, UnauthorizedAccess
from .schemas import AppInMongo


async def get_existed_app(
    app_id: PyObjectId, service=Provide(Container.AppsService)
) -> AppInMongo:
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
    client_id: UUID, service=Provide(Container.AppsService)
) -> AppInMongo:
    found_app = await service.get_by_client_id(client_id)
    if not found_app:
        raise AppNotFound()
    return found_app


ExistedAppByClientId = Annotated[AppInMongo, Depends(existed_app_by_client_id)]
