from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class TokenType(Enum):
    REFRESH = "refresh"
    ACCESS = "access"


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class TokenPayload(BaseModel):
    sub: int
    scopes: list[str]
    jti: str
    token_id: int


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    active: bool


class AuthSchema(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    email: EmailStr
    password: str = Field(
        min_length=3,
    )
