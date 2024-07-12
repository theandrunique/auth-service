from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, frozen=True)
class CreateAppDTO:
    name: str
    redirect_uris: list[str]
    scopes: list[str]
    creator_id: UUID
    description: str | None
    website: str | None


@dataclass(slots=True, frozen=True)
class AppUpdateInfoDTO:
    app_id: UUID
    name: str | None = None
    description: str | None = None
    redirect_uris: list[str] | None = None
    scopes: list[str] | None = None
    website: str | None = None


@dataclass(slots=True, frozen=True)
class OAuth2AppInfoDTO:
    client_id: UUID
    client_secret: UUID
    redirect_uris: list[str]
    scopes: list[str]
    is_authoritative: bool
