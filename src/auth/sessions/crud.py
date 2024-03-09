from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import UserSessionsInDB


async def get_sessions_from_db_by_user_id(
    user_id: int,
    session: AsyncSession,
) -> Sequence[UserSessionsInDB]:
    stmt = select(UserSessionsInDB).where(UserSessionsInDB.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().all()
