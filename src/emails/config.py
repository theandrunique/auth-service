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
    @property
    def RESET_TOKEN_EXPIRE_SECONDS(self) -> int:
        return self.RESET_TOKEN_EXPIRE_HOURS * 60 * 60

    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    @property
    def VERIFICATION_TOKEN_EXPIRE_SECONDS(self) -> int:
        return self.VERIFICATION_TOKEN_EXPIRE_HOURS * 60 * 60

    CONFIRM_FRONTEND_URI: str = "/email-confirm"

    OTP_EXPIRES_SECONDS: int = 60

    TEMPLATES_DIR: str = "email-templates"


settings = Settings()  # type: ignore
