from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4

from src.schemas import PyObjectId

from .repository import AppsRepository
from .schemas import AppCreate, AppInMongo


@dataclass(kw_only=True)
class AppsService:
    repository: AppsRepository

    async def add(self, new_app_data: AppCreate) -> AppInMongo:
        result = await self.repository.add(new_app_data.model_dump())
        return AppInMongo(id=result, **new_app_data.model_dump())

    async def get(self, id: PyObjectId) -> AppInMongo | None:
        found_app = await self.repository.get(id)
        if found_app:
            return AppInMongo(**found_app)
        return None

    async def get_by_client_id(self, client_id: UUID) -> AppInMongo | None:
        found_app = await self.repository.get_by_client_id(client_id)
        if found_app:
            return AppInMongo(**found_app)
        return None

    async def update(self, id: PyObjectId, new_values: dict[str, Any]) -> AppInMongo:
        updated_app = await self.repository.update(id, new_values)
        return AppInMongo(**updated_app)

    async def delete(self, id: PyObjectId) -> int:
        return await self.repository.delete(id)

    async def regenerate_client_secret(self, id: PyObjectId) -> AppInMongo:
        return await self.update(id, {"client_secret": uuid4()})
