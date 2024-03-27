from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    REFRESH_TOKEN_LENGTH = 120
    AUTHORIZATION_CODE_LENGTH = 120
    AUTHORIZATION_CODE_EXPIRE_SECONDS = 60


settings = Settings()
