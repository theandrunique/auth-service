from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel

from src.apps.schemas import Scope


class AuthoritativeApp(BaseModel):
    client_id: UUID
    client_secret: UUID
    redirect_uris: list[str]
    scopes: list[Scope]


@dataclass(kw_only=True)
class AuthoritativeAppsService:
    apps: list[AuthoritativeApp]

    def get_by_client_id(self, client_id: UUID) -> AuthoritativeApp | None:
        for app in self.apps:
            if app.client_id == client_id:
                return app
        return None
