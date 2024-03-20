import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .models import OAuth2SessionsInDB


async def create_oauth2_session(
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
        last_used=datetime.datetime.now(),
        created_at=datetime.datetime.now(),
    )
    session.add(oauth2_session)
    await session.commit()
    return oauth2_session
