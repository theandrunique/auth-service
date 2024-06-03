from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import AliasChoices, BaseModel, Field


class OAuth2SessionSchema(BaseModel):
    id: UUID = Field(validation_alias=AliasChoices("_id", "id"))
    user_id: UUID
    refresh_token_id: UUID
    app_id: UUID
    scopes: list[str]
    last_refresh: datetime
    created_at: datetime


class OAuth2SessionCreate(BaseModel):
    id: UUID = Field(default_factory=lambda: uuid4(), serialization_alias="_id")
    user_id: UUID
    refresh_token_id: UUID
    app_id: UUID
    scopes: list[str]
    last_refresh: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class OAuth2SessionCollection(BaseModel):
    auth_apps: list[OAuth2SessionSchema]
