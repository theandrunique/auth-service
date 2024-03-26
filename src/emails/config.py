from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    PORT: int = 465
    SERVER: str = "smtp.gmail.com"
    USER: str
    PASSWORD: str

    EMAILS_FROM_EMAIL: str
    EMAILS_FROM_NAME: str
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 24
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48


settings = Settings()  # type: ignore
