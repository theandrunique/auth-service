from pydantic import AnyUrl, RedisDsn
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

    SQLALCHEMY_DATABASE_URI: AnyUrl
    RedisURL: RedisDsn

    PRIVATE_KEY: str
    ALGORITHM: str = "RS256"
    USER_TOKEN_EXPIRE_HOURS: int = 30 * 24

    FRONTEND_URL: str = "http://localhost:5173"

    EMAILS_ENABLED: bool


settings = Settings()  # type: ignore
