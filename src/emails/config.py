from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    SMTP_PORT: int = 465
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_USER: str
    SMTP_PASSWORD: str

    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str
    RESET_PASSWORD_TOKEN_EXPIRE_SECONDS: int = 24 * 60 * 60
    EMAIL_VERIFICATION_TOKEN_EXPIRE_SECONDS: int = 48 * 60 * 60

    OTP_EXPIRES_SECONDS = 60

settings = Settings()  # type: ignore
