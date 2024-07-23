from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from src.oauth2_sessions.dto import CreateOAuth2SessionDTO
from src.oauth2_sessions.entities import OAuth2Session, OAuth2SessionFields

from .repository import IOAuth2SessionsRepository


class IOAuthSessionsService(ABC):
    @abstractmethod
    async def get(self, session_id: UUID) -> OAuth2Session | None: ...

    @abstractmethod
    async def get_by_token_id(self, token_id: UUID) -> OAuth2Session | None: ...

    @abstractmethod
    async def create_new_session(self, dto: CreateOAuth2SessionDTO) -> OAuth2Session: ...

    @abstractmethod
    async def update_token_id(self, session_id: UUID) -> UUID: ...

    @abstractmethod
    async def delete(self, session_id: UUID) -> None: ...

    @abstractmethod
    async def delete_all_by_user_id(self, user_id: UUID) -> None: ...


@dataclass(kw_only=True)
class OAuthSessionsService(IOAuthSessionsService):
    repository: IOAuth2SessionsRepository

    async def create_new_session(self, dto: CreateOAuth2SessionDTO) -> OAuth2Session:
        return await self.repository.add(
            OAuth2SessionFields(
                user_id=dto.user_id,
                client_id=dto.client_id,
                scopes=dto.scopes,
                token_id=uuid4(),
                last_refresh=datetime.now(),
                created_at=datetime.now(),
            )
        )

    async def get(self, session_id: UUID) -> OAuth2Session | None:
        return await self.repository.get_by_id(session_id)

    async def get_by_token_id(self, token_id: UUID) -> OAuth2Session | None:
        return await self.repository.get_by_token_id(token_id)

    async def update_token_id(self, session_id: UUID) -> UUID:
        new_token_id = uuid4()
        await self.repository.update_token_id_and_last_refresh(session_id, new_token_id, datetime.now())
        return new_token_id

    async def delete(self, session_id: UUID) -> None:
        await self.repository.delete_session(session_id)

    async def delete_all_by_user_id(self, user_id: UUID) -> None:
        await self.repository.delete_sessions(user_id)
