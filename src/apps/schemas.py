from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import AliasChoices, BaseModel, Field

from src.schemas import PyObjectId, Scope


class AppInMongo(BaseModel):
    id: PyObjectId = Field(validation_alias=AliasChoices("_id", "id"))
    name: str
    client_id: UUID
    client_secret: UUID
    redirect_uris: list[str] = Field(default_factory=list)
    scopes: list[Scope] = Field(default_factory=list)
    creator_id: UUID
    description: str | None = Field(default=None)
    website: str | None = Field(default=None)
    created_at: datetime


class AppCreate(BaseModel):
    name: str
    client_id: UUID = Field(default_factory=lambda: uuid4())
    client_secret: UUID = Field(default_factory=lambda: uuid4())
    redirect_uris: list[str] = Field(default_factory=list)
    scopes: list[Scope] = Field(default_factory=list)
    creator_id: UUID
    description: str | None = Field(default=None)
    website: str | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )


class AppPublicSchema(BaseModel):
    id: PyObjectId = Field(validation_alias=AliasChoices("_id", "id"))
    name: str
    client_id: UUID
    creator_id: UUID
    redirect_uris: list[str] = Field(default_factory=list)
    scopes: list[Scope] = Field(default_factory=list)
    description: str | None = Field(default=None)
    website: str | None = Field(default=None)
    created_at: datetime


class AppCreateSchema(BaseModel):
    name: str
    description: str | None = None
    redirect_uris: list[str] = Field(default_factory=list)
    scopes: list[Scope] = Field(default_factory=list)
    website: str | None = None


class AppUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    redirect_uris: list[str] | None = None
    scopes: list[Scope] | None = None
    website: str | None = None
