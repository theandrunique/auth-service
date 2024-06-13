from pydantic import MongoDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "Authorization Server"
    DOMAIN_URL: str

    RedisURL: RedisDsn

    PRIVATE_KEY: str
    ALGORITHM: str = "RS256"

    FRONTEND_URL: str = "http://localhost:5173"

    EMAILS_ENABLED: bool

    MONGO_DATABASE_NAME: str = "auth_server"
    MONGO_URI: MongoDsn

    SESSION_EXPIRE_HOURS: int = 24 * 30
    SESSION_KEY: str = "session"


settings = Settings()  # type: ignore
