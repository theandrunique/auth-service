import datetime
from uuid import UUID, uuid4

from pydantic import AliasChoices, BaseModel, Field


class AppInMongo(BaseModel):
    id: UUID = Field(
        default_factory=lambda: uuid4(),
        validation_alias=AliasChoices("_id", "id"),
        serialization_alias="_id",
    )
    name: str
    client_id: UUID = Field(default_factory=lambda: uuid4())
    client_secret: UUID = Field(default_factory=lambda: uuid4())
    redirect_uris: list[str]
    scopes: list[str] = Field(default=[])
    creator_id: int
    description: str | None = Field(default=None)
    website: str | None = Field(default=None)
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )


class AppPublic(BaseModel):
    id: UUID = Field(validation_alias=AliasChoices("_id", "id"))
    name: str
    client_id: UUID
    creator_id: int
    redirect_uris: list[str]
    scopes: list[str] = Field(default=[])
    description: str | None = Field(default=None)
    website: str | None = Field(default=None)
    created_at: datetime.datetime


class AppCreate(BaseModel):
    name: str
    description: str | None = None
    redirect_uris: list[str]
    scopes: list[str] = Field(default=[])
    website: str | None = None


class AppUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    redirect_uris: list[str] | None = None
    scopes: list[str] | None = None
    website: str | None = None
