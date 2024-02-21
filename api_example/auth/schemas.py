from pydantic import BaseModel, Field


class RefreshToken(BaseModel):
    refresh_token: str
    token_type: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class UserSchema(BaseModel):
    username: str
    active: bool


class AuthSchema(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    password: str = Field(min_length=3, )


class TokenData(BaseModel):
    user_id: int | None = None
    scopes: list[str] = []