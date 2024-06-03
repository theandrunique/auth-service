from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "Authorization Server"
    DOMAIN_URL: str = "http://localhost:8000"

    SQLALCHEMY_DATABASE_URI: AnyUrl

    PRIVATE_KEY: str
    ALGORITHM: str = "RS256"
    USER_TOKEN_EXPIRE_HOURS: int = 30 * 24
    KEYS_LENGTH: int = 40
    OTP_EXPIRE_SECONDS: int = 5 * 60

    FRONTEND_URL: str = "http://localhost:5173"

    EMAILS_ENABLED: bool


settings = Settings()  # type: ignore
