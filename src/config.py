from pydantic import AnyUrl, BaseModel, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class SmtpSettings(BaseModel):
    PORT: int = 465
    SERVER: str = "smtp.gmail.com"
    USER: str
    PASSWORD: str


class UsersSettings(BaseModel):
    USERNAME_MIN_LENGTH: int = 3
    USERNAME_MAX_LENGTH: int = 32

    USERNAME_PATTERN: str = r"^[a-zA-Z0-9_]+$"

    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 32

    PASSWORD_PATTERN: str = (
        r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
        extra="ignore",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "fastapi app"
    SERVER_HOST: str = "http://localhost"

    SQLALCHEMY_DATABASE_URI: AnyUrl

    SECRET_KEY: str = "secret_key"
    ALGORITHM: str = "HS256"
    USER_TOKEN_EXPIRE_HOURS: int = 30 * 24
    KEYS_LENGTH: int = 40
    OTP_EXPIRE_SECONDS: int = 5 * 60

    SMTP: SmtpSettings

    EMAILS_FROM_EMAIL: str
    EMAILS_FROM_NAME: str

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 24
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48

    REDIS_URL: RedisDsn
    MONGO_URL: str
    MONGO_DATABASE_NAME: str

    USERS: UsersSettings


settings = Settings()  # type: ignore
