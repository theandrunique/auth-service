from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import Response

from src import hash

from .repository import SessionsRepository
from .schemas import SessionCreate, SessionSchema
from .utils import gen_session_token, set_session


@dataclass(kw_only=True)
class SessionsService:
    repository: SessionsRepository

    async def create_session(self, user_id: UUID, res: Response) -> None:
        session_token = gen_session_token()
        item = SessionCreate(user_id=user_id, hashed_token=hash.create(session_token))
        await self.repository.add(item.model_dump(by_alias=True))
        set_session(
            key=str(item.id), token=session_token, expire=item.expires_at, res=res
        )

    async def get(self, key: UUID, token: str) -> SessionSchema | None:
        session = await self.repository.get(key)
        if not session:
            return None
        session = SessionSchema(**session)
        if not hash.check(value=token, hashed_value=session.hashed_token):
            return None
        return session

    async def get_many(self, count: int, offset: int) -> list[SessionSchema]:
        result = await self.repository.get_many(count=count, offset=offset)
        return [SessionSchema(**item) for item in result]

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
