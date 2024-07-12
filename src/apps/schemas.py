from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas import PyObjectId


class ApplicationSchema(BaseModel):
    id: PyObjectId
    name: str
    client_id: UUID
    creator_id: UUID
    redirect_uris: list[str] = Field(default_factory=list)
    scopes: list[str] = Field(default_factory=list)
    description: str | None = None
    website: str | None = None
    created_at: datetime
    client_secret: UUID


class AppCreateSchema(BaseModel):
    name: str
    description: str | None = None
    redirect_uris: list[str] = Field(default_factory=list)
    scopes: list[str] = Field(default_factory=list)
    website: str | None = None


class AppUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    redirect_uris: list[str] | None = None
    scopes: list[str] | None = None
    website: str | None = None
