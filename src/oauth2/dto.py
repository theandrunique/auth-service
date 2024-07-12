from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class TokenResponseDTO:
    access_token: str
    refresh_token: str
    scopes: list[str]
    token_type: str
    expires_in: int
