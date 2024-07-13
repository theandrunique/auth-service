from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, frozen=True)
class RegisterUserDTO:
    username: str
    email: str
    password: str


@dataclass(slots=True, frozen=True)
class UpdateUserPasswordDTO:
    user_id: UUID
    new_password: str
