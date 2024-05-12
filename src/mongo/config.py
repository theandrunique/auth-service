from pydantic import MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
        env_prefix="MONGO_",
    )
    DATABASE_NAME: str = "items"

    PING_ATTEMPTS: int = 5
    URI: MongoDsn


settings = MongoSettings()  # type: ignore
