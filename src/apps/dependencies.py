
from typing import Annotated

from fastapi import Depends
from pydantic import UUID4

from src.dependencies import UserAuthorization

from .exceptions import AppNotFound, UnauthorizedAccess
from .registry import AppsRegistry
from .schemas import AppInMongo


async def valid_app_id(app_id: UUID4) -> AppInMongo:
    found_app = await AppsRegistry.get(app_id)
    if not found_app:
        raise AppNotFound()
    return found_app

AppDep = Annotated[AppInMongo, Depends(valid_app_id)]


async def valid_access_app(app: AppDep, user: UserAuthorization) -> AppInMongo:
    if app.creator_id != user.id:
        raise UnauthorizedAccess()
    return app


AppAccessControlDep = Annotated[AppInMongo, Depends(valid_access_app)]
