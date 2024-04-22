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
    RESET_PASSWORD_TOKEN_EXPIRE_SECONDS: int = 24 * 60 * 60
    EMAIL_VERIFICATION_TOKEN_EXPIRE_SECONDS: int = 48 * 60 * 60
    EMAIL_CONFIRM_FRONTEND_URI: str = "/email-confirm"

    OTP_EXPIRES_SECONDS: int = 60

    TEMPLATES_DIR: str = "email-templates"


settings = Settings()  # type: ignore
