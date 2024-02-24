from enum import Enum
from pydantic import BaseModel, Field


class TokenType(Enum):
    REFRESH = "refresh"
    ACCESS = "access"


class RefreshToken(BaseModel):
    refresh_token: str
    token_type: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserSchema(BaseModel):
    username: str
    active: bool


class AuthSchema(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    password: str = Field(min_length=3, )
