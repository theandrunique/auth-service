from pydantic import RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
        env_prefix="REDIS_",
    )
    URL: RedisDsn
    PING_ATTEMPTS: int = 5


settings = RedisSettings()  # type: ignore
