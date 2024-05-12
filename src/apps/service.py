from dataclasses import dataclass
from typing import Any
from uuid import UUID

from .repository import AppsRepository
from .schemas import AppInMongo


@dataclass(kw_only=True)
class AppsService:
    repository: AppsRepository

    async def add(self, app: AppInMongo) -> AppInMongo:
        await self.repository.add(app.model_dump(by_alias=True))
        return app

    async def get(self, id: UUID) -> AppInMongo | None:
        found_app = await self.repository.get(id)
        if found_app:
            return AppInMongo(**found_app)
        return None

    async def get_by_client_id(self, client_id: UUID) -> AppInMongo | None:
        found_app = await self.repository.get_by_client_id(client_id)
        if found_app:
            return AppInMongo(**found_app)
        return None

    async def update(self, id: UUID, new_values: dict[str, Any]) -> AppInMongo:
        updated_app = await self.repository.update(id, new_values)
        return AppInMongo(**updated_app)

    async def delete(self, id: UUID) -> int:
        return await self.delete(id)
