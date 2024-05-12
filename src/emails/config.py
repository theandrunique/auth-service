from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
        env_prefix="EMAILS_",
    )

    SMTP_PORT: int
    SMTP_SERVER: str
    SMTP_USER: str
    SMTP_PASSWORD: str

    FROM_EMAIL: str
    FROM_NAME: str

    RESET_TOKEN_EXPIRE_HOURS: int = 24
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24

    CONFIRM_FRONTEND_URI: str = "/email-confirm"

    TEMPLATES_DIR: str = "email-templates"


settings = Settings()  # type: ignore
