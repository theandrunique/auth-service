from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "test app"
    SERVER_HOST: str = "http://localhost"

    DB_URL: str = "sqlite+aiosqlite:///auth.db"
    SECRET_KEY: str = "381fe4a2683cd0eee27cd66bfe1e5b02142ab7ee64d4f1ccbf1011e7358b005e"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 24 * 60
    KEYS_LENGTH: int = 40
    OTP_EXPIRE_SECONDS: int = 5 * 60

    SMTP_PORT: int = 465
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None

    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str | None = None

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 24
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48

    REDIS_HOST: str | None = None
    REDIS_PORT: int | None = None
    REDIS_PASSWORD: str | None = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
