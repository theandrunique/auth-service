from dataclasses import dataclass

from src.schemas import Scope


@dataclass(slots=True, frozen=True)
class TokenResponseDTO:
    access_token: str
    refresh_token: str
    scopes: list[str]
    token_type: str
    expires_in: int


@dataclass(slots=True, frozen=True)
class RequestValidateResponseDTO:
    requested_scopes: list[Scope]
