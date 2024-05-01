import datetime
from uuid import UUID, uuid4

from pydantic import AliasChoices, BaseModel, Field


class OAuth2SessionSchema(BaseModel):
    id: UUID = Field(validation_alias=AliasChoices("_id", "id"))
    refresh_token_hash: bytes
    app_id: UUID
    scopes: list[str]
    last_refresh: datetime.datetime
    created_at: datetime.datetime


class OAuth2SessionCreate(BaseModel):
    id: UUID = Field(default_factory=lambda: uuid4(), serialization_alias="_id")
    refresh_token_hash: bytes
    app_id: UUID
    scopes: list[str]
    last_refresh: datetime.datetime
    created_at: datetime.datetime


class OAuth2SessionCollection(BaseModel):
    auth_apps: list[OAuth2SessionSchema]
