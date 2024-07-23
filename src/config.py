from pydantic import BaseModel, MongoDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class SmtpSettings(BaseModel):
    SMTP_PORT: int
    SMTP_SERVER: str
    SMTP_USER: str
    SMTP_PASSWORD: str

    FROM_EMAIL: str
    FROM_NAME: str

    TEMPLATES_DIR: str = "templates"


class Settings(SmtpSettings, BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "Auth Service"
    DOMAIN_URL: str

    REDIS_URL: RedisDsn

    ALGORITHM: str = "RS256"

    FRONTEND_URL: str = "http://localhost:5173"

    EMAILS_ENABLED: bool

    MONGO_DATABASE_NAME: str = "auth_service"
    MONGO_URI: MongoDsn

    SESSION_EXPIRE_HOURS: int = 24 * 30
    SESSION_KEY: str = "session"

    AUTHORITATIVE_APPS_PATH: str = "/app/config/apps.json"
    CERT_DIR: str = "/app/config"


settings = Settings()  # type: ignore
