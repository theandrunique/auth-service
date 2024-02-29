from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "sqlite+aiosqlite:///auth.db"
    SECRET_KEY: str = "381fe4a2683cd0eee27cd66bfe1e5b02142ab7ee64d4f1ccbf1011e7358b005e"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 24 * 60
    REFRESH_TOKEN_LENGTH_BYTES: int = 24


settings = Settings()
