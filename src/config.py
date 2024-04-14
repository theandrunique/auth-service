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
    SERVER_HOST: str = "http://localhost"

    SQLALCHEMY_DATABASE_URI: AnyUrl

    SECRET_KEY: str = "secret_key"
    ALGORITHM: str = "HS256"
    USER_TOKEN_EXPIRE_HOURS: int = 30 * 24
    KEYS_LENGTH: int = 40
    OTP_EXPIRE_SECONDS: int = 5 * 60

    REDIS_URL: RedisDsn
    MONGO_URL: str
    MONGO_DATABASE_NAME: str
    FRONTEND_URL: str = "http://localhost:5173"


settings = Settings()  # type: ignore
