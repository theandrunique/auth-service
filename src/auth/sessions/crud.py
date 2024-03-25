import datetime
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import UserSessionsInDB
from src.config import settings


class SessionsDB:
    @staticmethod
    async def create_new(
        user_id: int,
        session_id: UUID,
        ip_address: str | None,
        session: AsyncSession,
    ) -> UserSessionsInDB:
        time_now = datetime.datetime.now()
        new_session = UserSessionsInDB(
            user_id=user_id,
            session_id=session_id,
            last_used=time_now,
            ip_address=ip_address,
            expires_at=time_now
            + datetime.timedelta(hours=settings.USER_TOKEN_EXPIRE_HOURS),
        )
        session.add(new_session)
        await session.commit()
        return new_session

    @staticmethod
    async def get(
        user_id: int,
        session_id: str,
        session: AsyncSession,
    ) -> UserSessionsInDB | None:
        stmt = (
            select(UserSessionsInDB)
            .where(UserSessionsInDB.user_id == user_id)
            .where(UserSessionsInDB.session_id == UUID(hex=session_id))
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_last_used(
        user_session: UserSessionsInDB,
        session: AsyncSession,
    ) -> None:
        user_session.last_used = datetime.datetime.now()
        session.add(user_session)
        await session.commit()


    @staticmethod
    async def get_by_user_id(
        user_id: int,
        session: AsyncSession,
    ) -> Sequence[UserSessionsInDB]:
        stmt = select(UserSessionsInDB).where(UserSessionsInDB.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().all()


    @staticmethod
    async def revoke(
        user_session: UserSessionsInDB,
        session: AsyncSession,
    ) -> None:
        await session.delete(user_session)
        await session.commit()


    @staticmethod
    async def revoke_by_id(
        user_id: int,
        session_id: UUID,
        session: AsyncSession,
    ) -> None:
        stmt = (
            delete(UserSessionsInDB)
            .where(UserSessionsInDB.user_id == user_id)
            .where(UserSessionsInDB.session_id == session_id)
        )
        await session.execute(stmt)
        await session.commit()


    @staticmethod
    async def revoke_by_ids(
        user_id: int,
        session_ids: list[UUID],
        session: AsyncSession,
    ) -> None:
        stmt = (
            delete(UserSessionsInDB)
            .where(UserSessionsInDB.user_id == user_id)
            .where(UserSessionsInDB.session_id.in_(session_ids))
        )
        await session.execute(stmt)
        await session.commit()


    @staticmethod
    async def revoke_except(
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
