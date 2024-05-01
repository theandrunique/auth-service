from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
        env_prefix="MONGO_",
    )
    USERNAME: str
    PASSWORD: str
    HOST: str = "localhost"
    PORT: int = 27017
    DATABASE_NAME: str

    PING_ATTEMPTS: int = 5

    @property
    def MONGO_URI(self) -> str:
        return f"mongodb://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}"


settings = MongoSettings()  # type: ignore
