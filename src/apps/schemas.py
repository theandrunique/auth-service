import datetime
from uuid import UUID, uuid4

import bson
from pydantic import AliasChoices, BaseModel, Field


def gen_bin_uuid():
    return bson.Binary.from_uuid(uuid4())


class AppMongoSchema(BaseModel):
    id: bytes = Field(
        default_factory=lambda: gen_bin_uuid(),
        alias="_id",
    )
    name: str
    client_id: bytes = Field(default_factory=lambda: gen_bin_uuid())
    client_secret: bytes = Field(default_factory=lambda: gen_bin_uuid())
    redirect_uri: str
    scopes: str | None = Field(default=None)
    creator_id: int
    description: str | None = Field(default=None)
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(),
    )


class AppPrivateSchema(BaseModel):
    id: UUID = Field(validation_alias=AliasChoices("_id", "id"))
    name: str
    client_id: UUID
    client_secret: UUID
    redirect_uri: str
    scopes: str | None = Field(default=None)
    creator_id: int
    description: str | None = Field(default=None)
    created_at: datetime.datetime


class AppPublicSchema(BaseModel):
    id: UUID = Field(validation_alias=AliasChoices("_id", "id"))
    name: str
    creator_id: int
    description: str | None = Field(default=None)
    created_at: datetime.datetime


class AppCreate(BaseModel):
    name: str
    description: str | None = None
    redirect_uri: str
    scopes: str | None = None


class AppUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    redirect_uri: str | None = None
    scopes: str | None = None
