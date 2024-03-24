import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class EmailTokenPayload(BaseModel):
    typ: str
    sub: str = Field(...)
    jti: UUID
    exp: datetime.datetime

    @field_validator("typ")
    @classmethod
    def check_type(cls, v: str) -> str:
        if v != "email":
            raise ValueError
        return v


class EmailToken(BaseModel):
    token: str
