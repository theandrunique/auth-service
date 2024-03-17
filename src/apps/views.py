from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, status
from pymongo import ReturnDocument

from src.auth.dependencies import UserAuthorization, UserAuthorizationOptional
from src.mongo_helper import db

from .exceptions import AppNotFound, UnauthorizedAccess
from .schemas import (
    AppCreate,
    AppMongoSchema,
    AppPublicSchema,
    AppUpdate,
)

router = APIRouter(prefix="", tags=["apps"])


app_collection = db["apps"]


@router.put("/{app_id}/regenerate-client-secret/", response_model=AppMongoSchema)
async def regenerate_client_secret(app_id: UUID, user: UserAuthorization) -> Any:
    found_app = await app_collection.find_one({"_id": app_id})
    if found_app is None:
        raise AppNotFound()
    app = AppMongoSchema(**found_app)
    if app.creator_id != user.id:
        raise UnauthorizedAccess()
    app.client_secret = uuid4()
    await app_collection.update_one(
        {"_id": app_id}, {"$set": {"client_secret": app.client_secret}}
    )
    return app


@router.post("/", response_model=AppMongoSchema, status_code=status.HTTP_201_CREATED)
async def create_app(app: AppCreate, user: UserAuthorization) -> Any:
    new_app = AppMongoSchema(**app.model_dump(), creator_id=user.id)
    await app_collection.insert_one(new_app.model_dump(by_alias=True))
    return new_app


@router.get("/{app_id}/")
async def get_app_by_id(
    app_id: UUID, user: UserAuthorizationOptional
) -> AppMongoSchema | AppPublicSchema:
    found_app = await app_collection.find_one({"_id": app_id})
    if found_app is None:
        raise AppNotFound()
    app = AppMongoSchema(**found_app)

    if user and app.creator_id == user.id:
        return app

    return AppPublicSchema(**app.model_dump())


@router.patch("/{app_id}/")
async def update_app(
    app_id: UUID, data: AppUpdate, user: UserAuthorization
) -> AppMongoSchema:
    new_values = data.model_dump(exclude_defaults=True)

    found_app = await app_collection.find_one({"_id": app_id})
    if found_app is None:
        raise AppNotFound()

    app = AppMongoSchema(**found_app)

    if app.creator_id != user.id:
        raise UnauthorizedAccess()

    if new_values:
        updated_app = await app_collection.find_one_and_update(
            {"_id": app_id},
            {"$set": new_values},
            return_document=ReturnDocument.AFTER,
        )
        return AppMongoSchema(**updated_app)
    else:
        return app


@router.delete("/{app_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app(app_id: UUID, user: UserAuthorization) -> None:
    found_app = await app_collection.find_one({"_id": app_id})
    if found_app is None:
        raise AppNotFound()

    app = AppMongoSchema(**found_app)

    if app.creator_id != user.id:
        raise UnauthorizedAccess()

    await app_collection.delete_one({"_id": app_id})
