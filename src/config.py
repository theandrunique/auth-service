from pydantic import BaseModel, MongoDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class OAuthSettings(BaseModel):
    AUTHORIZATION_CODE_LENGTH: int = 512
    AUTHORIZATION_CODE_EXPIRE_SECONDS: int = 60
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 3600
    REFRESH_TOKEN_EXPIRE_HOURS: int = 24


class UsersSettings(BaseModel):
    USERNAME_MIN_LENGTH: int = 3
    USERNAME_MAX_LENGTH: int = 32

    USERNAME_PATTERN: str = r"^[a-zA-Z0-9_]+$"

    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 32

    PASSWORD_PATTERN: str = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])+"


class SmtpSettings(BaseModel):
    SMTP_PORT: int
    SMTP_SERVER: str
    SMTP_USER: str
    SMTP_PASSWORD: str

    FROM_EMAIL: str
    FROM_NAME: str

    TEMPLATES_DIR: str = "templates"


class Settings(SmtpSettings, UsersSettings, OAuthSettings, BaseSettings):
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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = True


settings = Settings()  # type: ignore
