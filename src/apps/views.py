from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pymongo import ReturnDocument

from src.mongo_helper import db

from .schemas import AppCreate, AppMongoSchema, AppSchema, AppUpdate

router = APIRouter(prefix="", tags=["apps"])


app_collection = db["apps"]


@router.post("/", response_model=AppSchema)
async def create_app(app: AppCreate):
    new_app = AppMongoSchema(**app.model_dump(), creator_id=1)
    await app_collection.insert_one(new_app.model_dump(by_alias=True))
    return new_app


@router.get("/{app_id}/")
async def get_app_by_id(app_id: UUID):
    app = await app_collection.find_one({"_id": app_id})
    if app is None:
        raise HTTPException(status_code=404, detail=f"App {app_id} not found")
    return AppSchema(**app)


@router.patch("/{app_id}/")
async def update_app(app_id: UUID, data: AppUpdate):
    new_values = data.model_dump(exclude_defaults=True)

    if new_values:
        updated_app = await app_collection.find_one_and_update(
            {"_id": app_id},
            {"$set": new_values},
            return_document=ReturnDocument.AFTER,
        )
        if updated_app is None:
            raise HTTPException(status_code=404, detail=f"App {app_id} not found")
        return AppSchema(**updated_app)
    else:
        return AppSchema(**await app_collection.find_one({"_id": app_id}))


@router.delete("/{app_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app(app_id: UUID):
    delete_result = await app_collection.delete_one({"_id": app_id})
    if delete_result.deleted_count != 1:
        raise HTTPException(status_code=404, detail=f"App {app_id} not found")
