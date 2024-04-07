from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    REFRESH_TOKEN_LENGTH: int = 120
    AUTHORIZATION_CODE_LENGTH: int = 120
    AUTHORIZATION_CODE_EXPIRE_SECONDS: int = 60
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 3600


settings = Settings()
