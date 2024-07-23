from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)


class UserSchema(BaseModel):
    id: UUID
    username: str
    email: str
    email_verified: bool
    image_url: str | None = Field(default=None)
    active: bool
    created_at: datetime
