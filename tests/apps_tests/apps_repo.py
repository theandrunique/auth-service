from uuid import UUID, uuid4

from src.apps.dto import AppUpdateInfoDTO
from src.apps.entities import Application
from src.apps.repository import IAppsRepository


class InMemoryAppsRepository(IAppsRepository):
    def __init__(self):
        self.apps: dict[UUID, Application] = {}

    async def get(self, id: UUID) -> Application | None:
        return self.apps.get(id)

    async def get_by_client_id(self, client_id: UUID) -> Application | None:
        return next((app for app in self.apps.values() if app.client_id == client_id), None)

    async def add(self, app: Application) -> Application:
        if app.id is None:
            app.id = uuid4()

        self.apps[app.id] = app
        return app

    async def update_client_secret(self, app_id: UUID, client_secret: UUID) -> Application:
        app = self.apps[app_id]
        app.client_secret = client_secret
        return app

    async def delete(self, id: UUID) -> None:
        if id in self.apps:
            del self.apps[id]

    async def update_app_info(self, dto: AppUpdateInfoDTO) -> Application:
        app = self.apps[dto.app_id]
        if dto.name is not None:
            app.name = dto.name
        if dto.description is not None:
            app.description = dto.description
        if dto.redirect_uris is not None:
            app.redirect_uris = dto.redirect_uris
        if dto.scopes is not None:
            app.scopes = dto.scopes
        if dto.website is not None:
            app.website = dto.website
        return app
