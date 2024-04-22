from typing import Any
from uuid import UUID

from src.apps.schemas import AppInMongo
from src.mongo.base_repository import Repository


class FakeAppsRepository(Repository):
    def __init__(self) -> None:
        self.app_collection: dict[UUID, dict[str, Any]] = {}

    async def add(self, app: AppInMongo) -> UUID:
        self.app_collection[app.id] = app.model_dump(by_alias=True)
        return app.id

    async def get(self, id: UUID) -> AppInMongo | None:
        found_app = self.app_collection.get(id)
        if found_app:
            return AppInMongo(**found_app)
        return None

    async def get_many(self, count: int, offset: int) -> list[Any]:
        raise NotImplementedError()

    async def get_by_client_id(self, client_id: UUID) -> AppInMongo | None:
        for app_data in self.app_collection.values():
            if app_data.get("client_id") == client_id:
                return AppInMongo(**app_data)
        return None

    async def delete(self, id: UUID) -> int:
        if id in self.app_collection:
            del self.app_collection[id]
            return 1
        return 0

    async def update(self, id: UUID, new_values: dict[str, Any]) -> AppInMongo:
        if id in self.app_collection:
            self.app_collection[id].update(new_values)
            return AppInMongo(**self.app_collection[id])
        raise Exception("App not found")

    async def update_optional(
        self, id: UUID, new_values: dict[str, Any]
    ) -> AppInMongo | None:
        if id in self.app_collection:
            self.app_collection[id].update(new_values)
            return AppInMongo(**self.app_collection[id])
        return None
