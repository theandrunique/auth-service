from dataclasses import dataclass
from uuid import UUID

from src.schemas import AuthoritativeApp


@dataclass(kw_only=True)
class AuthoritativeAppsService:
    apps: dict[UUID, AuthoritativeApp]

    def get_by_client_id(self, client_id: UUID) -> AuthoritativeApp | None:
        return self.apps.get(client_id)
