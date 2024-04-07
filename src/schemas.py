import datetime

from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    sub: str
    scopes: list[str]
    exp: datetime.datetime
    oauth2: bool = Field(default=True)
