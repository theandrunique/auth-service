from typing import Any
from uuid import UUID

from fastapi import APIRouter, status
from pymongo import ReturnDocument

from src.auth.dependencies import UserAuthorization, UserAuthorizationOptional
from src.mongo_helper import db

from .exceptions import AppNotFound, UnauthorizedAccess
from .schemas import (
    AppCreate,
    AppMongoSchema,
    AppPrivateSchema,
    AppPublicSchema,
    AppUpdate,
)

router = APIRouter(prefix="", tags=["apps"])


app_collection = db["apps"]


@router.post("/", response_model=AppPrivateSchema)
async def create_app(app: AppCreate, user: UserAuthorization) -> Any:
    new_app = AppMongoSchema(**app.model_dump(), creator_id=user.id)
    await app_collection.insert_one(new_app.model_dump(by_alias=True))
    return new_app


@router.get("/{app_id}/")
async def get_app_by_id(
    app_id: UUID, user: UserAuthorizationOptional
) -> AppPrivateSchema | AppPublicSchema:
    found_app = await app_collection.find_one({"_id": app_id})
    if found_app is None:
        raise AppNotFound()
    app = AppPrivateSchema(**found_app)

    if user and app.creator_id == user.id:
        return app

    return AppPublicSchema(**app.model_dump())


@router.patch("/{app_id}/")
async def update_app(
    app_id: UUID, data: AppUpdate, user: UserAuthorization
) -> AppPrivateSchema:
    new_values = data.model_dump(exclude_defaults=True)

    found_app = await app_collection.find_one({"_id": app_id})
    if found_app is None:
        raise AppNotFound()

    app = AppPrivateSchema(**found_app)

    if app.creator_id != user.id:
        raise UnauthorizedAccess()

    if new_values:
        updated_app = await app_collection.find_one_and_update(
            {"_id": app_id},
            {"$set": new_values},
            return_document=ReturnDocument.AFTER,
        )
        return AppPrivateSchema(**updated_app)
    else:
        return app


@router.delete("/{app_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app(app_id: UUID, user: UserAuthorization) -> None:
    found_app = await app_collection.find_one({"_id": app_id})
    if found_app is None:
        raise AppNotFound()

    app = AppPrivateSchema(**found_app)

    if app.creator_id != user.id:
        raise UnauthorizedAccess()

    await app_collection.delete_one({"_id": app_id})
