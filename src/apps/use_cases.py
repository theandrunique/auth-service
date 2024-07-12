from dataclasses import dataclass
from uuid import UUID

from src.apps.dto import AppUpdateInfoDTO, CreateAppDTO
from src.apps.entities import Application
from src.apps.exceptions import AppNotFound
from src.apps.service import IAppsService
from src.users.entities import User


@dataclass
class CreateAppCommand:
    user: User
    name: str
    redirect_uris: list[str]
    scopes: list[str]
    description: str | None
    website: str | None


@dataclass
class CreateAppUseCase:
    apps_service: IAppsService

    async def execute(self, command: CreateAppCommand) -> Application:
        assert command.user.id

        return await self.apps_service.create_new_app(
            CreateAppDTO(
                name=command.name,
                redirect_uris=command.redirect_uris,
                scopes=command.scopes,
                description=command.description,
                website=command.website,
                creator_id=command.user.id,
            )
        )


@dataclass
class GetUserAppsCommand:
    user: User


@dataclass
class GetUserAppsUseCase:
    apps_service: IAppsService

    async def execute(self, command: GetUserAppsCommand) -> list[Application]:
        assert command.user.id
        return await self.apps_service.get_all_by_user_id(command.user.id)


@dataclass
class RegenerateClientSecretCommand:
    user: User
    app_id: UUID


@dataclass
class RegenerateClientSecretUseCase:
    apps_service: IAppsService

    async def execute(self, command: RegenerateClientSecretCommand) -> Application:
        assert command.user.id

        app = await self.apps_service.get(command.app_id)
        if not app:
            raise AppNotFound

        self.apps_service.validate_access(command.user.id, app)

        assert app.id
        return await self.apps_service.regenerate_client_secret(app.id)


@dataclass
class UpdateAppInfoCommand:
    user: User
    app_id: UUID
    name: str | None = None
    description: str | None = None
    redirect_uris: list[str] | None = None
    scopes: list[str] | None = None
    website: str | None = None


class UpdateAppInfoUseCase:
    apps_service: IAppsService

    async def execute(self, command: UpdateAppInfoCommand) -> Application:
        assert command.user.id

        app = await self.apps_service.get(command.app_id)
        if not app:
            raise AppNotFound
        assert app.id

        self.apps_service.validate_access(command.user.id, app)
        return await self.apps_service.update_app_info(
            AppUpdateInfoDTO(
                app_id=app.id,
                name=command.name,
                description=command.description,
                redirect_uris=command.redirect_uris,
                scopes=command.scopes,
                website=command.website,
            )
        )
