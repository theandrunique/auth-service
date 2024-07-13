from abc import ABC, abstractmethod
from uuid import UUID

from src.apps.dto import AppUpdateInfoDTO
from src.apps.entities import Application, ApplicationFields
from src.apps.models import AppODM


class IAppsRepository(ABC):
    @abstractmethod
    async def get(self, id: UUID) -> Application | None: ...

    @abstractmethod
    async def get_by_client_id(self, client_id: UUID) -> Application | None: ...

    @abstractmethod
    async def get_apps_by_user_id(self, user_id: UUID) -> list[Application]: ...

    @abstractmethod
    async def add(self, app: ApplicationFields) -> Application: ...

    @abstractmethod
    async def update_client_secret(self, app_id: UUID, client_secret: UUID) -> Application: ...

    @abstractmethod
    async def delete(self, id: UUID) -> None: ...

    @abstractmethod
    async def update_app_info(self, dto: AppUpdateInfoDTO) -> Application: ...


class MongoAppsRepository(IAppsRepository):
    async def get(self, id: UUID) -> Application | None:
        app_model = await AppODM.find_one(AppODM.id == id)
        if app_model is None:
            return None
        return app_model.to_entity()

    async def get_apps_by_user_id(self, user_id: UUID) -> list[Application]:
        apps = await AppODM.find_many(AppODM.creator_id == user_id).to_list(None)
        return [app.to_entity() for app in apps]

    async def get_by_client_id(self, client_id: UUID) -> Application | None:
        app_model = await AppODM.find_one(AppODM.client_id == client_id)
        if app_model is None:
            return None
        return app_model.to_entity()

    async def add(self, app: ApplicationFields) -> Application:
        app_model = AppODM.from_fields(app)
        await app_model.insert()
        return app_model.to_entity()

    async def update_client_secret(self, app_id: UUID, client_secret: UUID) -> Application:
        app_model = await AppODM.find_one(AppODM.id == app_id)
        if not app_model:
            raise Exception("App not found")

        app_model.client_secret = client_secret
        await app_model.save()
        return app_model.to_entity()

    async def delete(self, id: UUID) -> None:
        await AppODM.find_one(AppODM.id == id).delete()

    async def update_app_info(self, dto: AppUpdateInfoDTO) -> Application:
        app = await AppODM.find_one(AppODM.id == dto.app_id)
        if not app:
            raise Exception("App not found")

        if dto.name:
            app.name = dto.name
        if dto.description:
            app.description = dto.description
        if dto.redirect_uris:
            app.redirect_uris = dto.redirect_uris
        if dto.scopes:
            app.scopes = dto.scopes
        if dto.website:
            app.website = dto.website

        await app.save()
        return app.to_entity()
