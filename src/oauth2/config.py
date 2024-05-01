from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
        env_prefix="OAUTH2_",
    )

    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    REFRESH_TOKEN_BYTES_LENGTH: int = 120
    REFRESH_TOKEN_EXPIRE_HOURS: int = 24 * 7
    AUTHORIZATION_CODE_LENGTH: int = 120
    AUTHORIZATION_CODE_EXPIRE_SECONDS: int = 60
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 3600


settings = Settings()  # type: ignore
