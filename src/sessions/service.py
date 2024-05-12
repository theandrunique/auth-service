from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from src.mongo import db
from src.sessions.schemas import SessionCreate, SessionSchema

from .repository import SessionsRepository


@dataclass(kw_only=True)
class SessionsService:
    repository: SessionsRepository

    async def add(self, item: SessionCreate) -> SessionSchema:
        await self.repository.add(item.model_dump(by_alias=True))
        return SessionSchema(**item.model_dump())

    async def get_many(self, count: int, offset: int) -> list[SessionSchema]:
        result = await self.repository.get_many(count=count, offset=offset)
        return [SessionSchema(**item) for item in result]

    async def get(self, id: UUID) -> SessionSchema | None:
        found = await self.repository.get(id)
        if found:
            return SessionSchema(**found)
        return None

    async def update(self, id: UUID, new_values: dict[str, Any]) -> SessionSchema:
        updated = await self.repository.update(id, new_values)
        return SessionSchema(**updated)

    async def update_last_used(self, id: UUID) -> None:
        await self.repository.update(id=id, new_values={"last_used": datetime.now(UTC)})

    async def delete(self, id: UUID) -> int:
        return await self.repository.delete(id)

    async def delete_expired_sessions(self) -> int:
        return await self.repository.delete_expired_sessions()

    async def delete_except(self, except_id: UUID) -> int:
        return await self.repository.delete_except(except_id)

    async def delete_all(self) -> None:
        await self.repository.delete_all()


def sessions_service_factory(user_id: UUID) -> SessionsService:
    return SessionsService(
        repository=SessionsRepository(
            collection=db[f"sessions_{user_id.hex}"],
        )
    )
