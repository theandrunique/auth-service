from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel


class AuthoritativeApp(BaseModel):
    client_id: UUID
    client_secret: UUID
    redirect_uris: list[str]
    scopes: list[str]


authoritative_apps = {
    UUID("5353554b-557e-4872-976e-baf669b2c708"): AuthoritativeApp(
        client_id=UUID("5353554b-557e-4872-976e-baf669b2c708"),
        client_secret=UUID("1dc18d7b-6ff4-4319-953d-b27bc246d3ff"),
        redirect_uris=["http://example.com"],
        scopes=["user-info"],
    )
}


@dataclass(kw_only=True)
class AuthoritativeAppsService:
    apps: dict[UUID, AuthoritativeApp]

    def get_by_client_id(self, client_id: UUID) -> AuthoritativeApp | None:
        return authoritative_apps.get(client_id)


apps_service = AuthoritativeAppsService(apps=authoritative_apps)
