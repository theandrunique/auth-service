from pydantic import AnyUrl, BaseModel, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class SmtpSettings(BaseModel):
    PORT: int = 465
    SERVER: str = "smtp.gmail.com"
    USER: str
    PASSWORD: str

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
        extra="ignore",
        case_sensitive=True
    )

    PROJECT_NAME: str = "fastapi app"
    SERVER_HOST: str = "http://localhost"

    SQLALCHEMY_DATABASE_URI: AnyUrl

    SECRET_KEY: str = "secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 24 * 60
    KEYS_LENGTH: int = 40
    OTP_EXPIRE_SECONDS: int = 5 * 60

    SMTP: SmtpSettings

    EMAILS_FROM_EMAIL: str
    EMAILS_FROM_NAME: str

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 24
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48

    REDIS_URL: RedisDsn


settings = Settings() # type: ignore
