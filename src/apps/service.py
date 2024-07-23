from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from src.apps.dto import AppUpdateInfoDTO, CreateAppDTO, OAuth2AppInfoDTO
from src.apps.entities import Application, ApplicationFields
from src.exceptions import ServiceError, ServiceErrorCode
from src.schemas import AuthoritativeApp
from src.services.authoritative_apps import AuthoritativeAppsService

from .repository import IAppsRepository


@dataclass
class IAppsService(ABC):
    @abstractmethod
    async def create_new_app(self, dto: CreateAppDTO) -> Application: ...

    @abstractmethod
    async def get(self, app_id: UUID) -> Application | None: ...

    @abstractmethod
    async def get_all_by_user_id(self, user_id: UUID) -> list[Application]: ...

    @abstractmethod
    async def get_by_client_id(self, client_id: UUID) -> OAuth2AppInfoDTO | None: ...

    @abstractmethod
    async def delete(self, app_id: UUID) -> None: ...

    @abstractmethod
    async def regenerate_client_secret(self, app_id: UUID) -> Application: ...

    @abstractmethod
    async def update_app_info(self, dto: AppUpdateInfoDTO) -> Application: ...

    @abstractmethod
    def validate_access(self, user_id: UUID, app: Application) -> None: ...


@dataclass
class AppsService(IAppsService):
    repository: IAppsRepository
    authoritative_apps: AuthoritativeAppsService

    async def create_new_app(self, dto: CreateAppDTO) -> Application:
        return await self.repository.add(
            ApplicationFields(
                name=dto.name,
                client_id=uuid4(),
                client_secret=uuid4(),
                redirect_uris=dto.redirect_uris,
                scopes=dto.scopes,
                creator_id=dto.creator_id,
                description=dto.description,
                website=dto.website,
                created_at=datetime.now(),
                is_web_message_allowed=False,
            )
        )

    async def get_all_by_user_id(self, user_id: UUID) -> list[Application]:
        apps = await self.repository.get_apps_by_user_id(user_id)
        return apps

    async def get(self, app_id: UUID) -> Application | None:
        return await self.repository.get(app_id)

    async def get_by_client_id(self, client_id: UUID) -> OAuth2AppInfoDTO | None:
        app = self.authoritative_apps.get_by_client_id(client_id)
        if not app:
            app = await self.repository.get_by_client_id(client_id)
        if not app:
            return None
        return OAuth2AppInfoDTO(
            client_id=app.client_id,
            client_secret=app.client_secret,
            redirect_uris=app.redirect_uris,
            scopes=app.scopes,
            is_authoritative=isinstance(app, AuthoritativeApp),
        )

    async def delete(self, app_id: UUID) -> None:
        await self.repository.delete(app_id)

    async def regenerate_client_secret(self, app_id: UUID) -> Application:
        new_client_secret = uuid4()
        return await self.repository.update_client_secret(app_id, new_client_secret)

    async def update_app_info(self, dto: AppUpdateInfoDTO) -> Application:
        return await self.repository.update_app_info(dto)

    def validate_access(self, user_id: UUID, app: Application) -> None:
        if app.creator_id != user_id:
            raise ServiceError(code=ServiceErrorCode.INSUFFICIENT_PERMISSIONS)
