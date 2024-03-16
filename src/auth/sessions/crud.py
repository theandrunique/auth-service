from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import UserSessionsInDB


async def get_sessions_from_db_by_user_id(
    user_id: int,
    session: AsyncSession,
) -> Sequence[UserSessionsInDB]:
    stmt = select(UserSessionsInDB).where(UserSessionsInDB.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def revoke_user_session(
    user_session: UserSessionsInDB,
    session: AsyncSession,
) -> None:
    await session.delete(user_session)
    await session.commit()


async def revoke_user_sessions_by_id(
    user_id: int,
    session_id: UUID,
    session: AsyncSession,
) -> None:
    stmt = delete(UserSessionsInDB).where(UserSessionsInDB.session_id == session_id)
    await session.execute(stmt)
    await session.commit()


async def revoke_user_sessions_except_current(
    user_id: int,
    except_id: UUID,
    session: AsyncSession,
) -> None:
    stmt = (
        delete(UserSessionsInDB)
        .where(UserSessionsInDB.user_id == user_id)
        .where(UserSessionsInDB.session_id != except_id)
    )
    await session.execute(stmt)
    await session.commit()
