from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.dependencies import UserAuthorization

from .exceptions import AppNotFound, UnauthorizedAccess
from .repository import repository
from .schemas import AppInMongo


async def valid_app_id(app_id: UUID) -> AppInMongo:
    found_app = await repository.get(app_id)
    if not found_app:
        raise AppNotFound()
    return found_app


AppDep = Annotated[AppInMongo, Depends(valid_app_id)]


async def valid_access_app(app: AppDep, user: UserAuthorization) -> AppInMongo:
    if app.creator_id != user.id:
        raise UnauthorizedAccess()
    return app


AppAccessControlDep = Annotated[AppInMongo, Depends(valid_access_app)]


async def existed_app_by_client_id(client_id: UUID) -> AppInMongo:
    found_app = await repository.get_by_client_id(client_id)
    if not found_app:
        raise AppNotFound()
    return found_app


ExistedAppByClientId = Annotated[AppInMongo, Depends(existed_app_by_client_id)]
