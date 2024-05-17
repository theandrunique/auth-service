from pydantic_settings import BaseSettings, SettingsConfigDict


class SessionsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
        env_prefix="SESSIONS_",
    )
    EXPIRE_HOURS: int = 24 * 30
    TOKEN_BYTES_LENGTH: int = 32

    ID_KEY: str = "session_key"
    VALUE_KEY: str = "session"


settings = SessionsSettings()
