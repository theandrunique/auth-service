from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True, slots=True)
class CreateOAuth2SessionDTO:
    user_id: UUID
    client_id: UUID
    scopes: list[str]
