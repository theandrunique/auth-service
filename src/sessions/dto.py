from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateSessionDTO:
    user_id: UUID
    ip_address: str
