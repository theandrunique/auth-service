import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import OAuth2SessionsInDB
from .utils import get_bytes_from_token, hash_token


class OAuth2SessionsDB:
    @staticmethod
    async def create_session(
        user_id: int,
        session_id: UUID,
        refresh_token_hash: bytes,
        app_id: UUID,
        scope: str,
        session: AsyncSession,
    ) -> OAuth2SessionsInDB:
        oauth2_session = OAuth2SessionsInDB(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            session_id=session_id,
            app_id=app_id,
            scope=scope,
            last_used=datetime.datetime.now(datetime.timezone.utc),
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        session.add(oauth2_session)
        await session.commit()
        return oauth2_session

    @staticmethod
    async def get_by_token(
        token: str, session: AsyncSession
    ) -> OAuth2SessionsInDB | None:
        token_bytes = hash_token(get_bytes_from_token(token))
        stmt = select(OAuth2SessionsInDB).where(
            OAuth2SessionsInDB.refresh_token_hash == hash_token(token_bytes)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update(
        oauth2_session: OAuth2SessionsInDB,
        refresh_token_hash: bytes,
        session: AsyncSession,
    ) -> None:
        oauth2_session.last_used = datetime.datetime.now(datetime.timezone.utc)
        oauth2_session.refresh_token_hash = refresh_token_hash
        await session.commit()
