from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from .entities import OAuth2Session, OAuth2SessionFields
from .models import OAuth2SessionODM


class IOAuth2SessionsRepository(ABC):
    @abstractmethod
    async def add(self, session: OAuth2SessionFields) -> OAuth2Session: ...

    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> OAuth2Session | None: ...

    @abstractmethod
    async def get_by_token_id(self, token_id: UUID) -> OAuth2Session | None: ...

    @abstractmethod
    async def update_token_id_and_last_refresh(
        self, session_id: UUID, token_id: UUID, last_refresh: datetime
    ) -> None: ...

    @abstractmethod
    async def delete_session(self, session_id: UUID) -> OAuth2Session | None: ...

    @abstractmethod
    async def delete_sessions(self, user_id: UUID) -> None: ...


class MongoOAuth2SessionsRepository(IOAuth2SessionsRepository):
    async def add(self, session: OAuth2SessionFields) -> OAuth2Session:
        session_model = OAuth2SessionODM.from_fields(session)
        await session_model.insert()
        return session_model.to_entity()

    async def get_by_id(self, session_id: UUID) -> OAuth2Session | None:
        session_model = await OAuth2SessionODM.find_one(OAuth2SessionODM.id == session_id)
        if session_model is None:
            return None
        return session_model.to_entity()

    async def get_by_token_id(self, token_id: UUID) -> OAuth2Session | None:
        session = await OAuth2SessionODM.find_one(OAuth2SessionODM.token_id == token_id)
        if session is None:
            return None
        return session.to_entity()

    async def update_token_id_and_last_refresh(self, session_id: UUID, token_id: UUID, last_refresh: datetime) -> None:
        session = await OAuth2SessionODM.find_one(OAuth2SessionODM.id == session_id)
        if session is None:
            raise Exception("Session not found")

        session.token_id = token_id
        session.last_refresh = last_refresh
        await session.save()

    async def delete_session(self, session_id: UUID) -> None:
        session = await OAuth2SessionODM.find_one(OAuth2SessionODM.id == session_id)
        if session is None:
            return None
        await session.delete()

    async def delete_sessions(self, user_id: UUID) -> None:
        await OAuth2SessionODM.find_many(OAuth2SessionODM.user_id == user_id).delete()
