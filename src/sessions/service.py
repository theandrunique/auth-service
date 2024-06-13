from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import Request, Response

from src.dependencies import Container, resolve

from .repository import SessionsRepository
from .schemas import SessionCreate, SessionSchema
from .utils import delete_session_cookie, set_session_cookie


@dataclass(kw_only=True)
class SessionsService:
    repository: SessionsRepository

    async def create_session(self, user_id: UUID, res: Response, req: Request) -> None:
        item = SessionCreate(
            user_id=user_id, ip_address=req.client.host if req.client else None
        )
        jwe_service = resolve(Container.JWE)
        await self.repository.add(item.model_dump(by_alias=True))
        session_token = jwe_service.encode(item.id.bytes)
        set_session_cookie(token=session_token, expire=item.expires_at, res=res)

    async def get(self, token: str) -> SessionSchema | None:
        jwe_service = resolve(Container.JWE)
        session_id_bytes = jwe_service.decode(token)
        if not session_id_bytes:
            return None

        session_id = UUID(bytes=session_id_bytes)

        session = await self.repository.get(session_id)
        if not session:
            return None
        session = SessionSchema(**session)
        return session

    async def get_many(
        self, user_id: UUID, count: int, offset: int
    ) -> list[SessionSchema]:
        result = await self.repository.get_many_by_user(
            user_id=user_id, count=count, offset=offset
        )
        return [SessionSchema(**item) for item in result]

    async def update(self, id: UUID, new_values: dict[str, Any]) -> SessionSchema:
        updated = await self.repository.update(id, new_values)
        return SessionSchema(**updated)

    async def update_last_used(self, id: UUID) -> None:
        await self.repository.update(id=id, new_values={"last_used": datetime.now(UTC)})

    async def delete(self, id: UUID, res: Response) -> int:
        delete_session_cookie(res)
        return await self.repository.delete(id)

    async def delete_expired_sessions(self) -> int:
        return await self.repository.delete_expired_sessions()

    async def delete_except(self, except_id: UUID) -> int:
        return await self.repository.delete_except(except_id)

    async def delete_all(self, user_id: UUID) -> None:
        await self.repository.delete_all(user_id=user_id)
