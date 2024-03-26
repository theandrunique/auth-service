from pydantic import BaseModel


class Settings(BaseModel):
    USERNAME_MIN_LENGTH: int = 3
    USERNAME_MAX_LENGTH: int = 32

    USERNAME_PATTERN: str = r"^[a-zA-Z0-9_]+$"

    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 32

    PASSWORD_PATTERN: str = (
        r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
    )

settings = Settings()  # type: ignore
