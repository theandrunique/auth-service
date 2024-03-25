import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models import UserInDB

from .models import UserSessionsInDB
from .utils import hash_password


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


class UsersDB:
    async def create_new(
        username: str,
        password: str,
        email: str,
        session: AsyncSession,
    ) -> UserInDB:
        new_user = UserInDB(
            username=username,
            hashed_password=hash_password(password),
            email=email,
            created_at=datetime.datetime.now(),
        )
        session.add(new_user)
        await session.commit()
        return new_user

    async def get_by_id(id: int, session: AsyncSession) -> UserInDB | None:
        return await session.get(UserInDB, ident=id)

    @staticmethod
    async def get_with_session(
        user_id: int,
        session_id: str,
        session: AsyncSession,
    ) -> tuple[UserInDB | None, UserSessionsInDB | None]:
        stmt = (
            select(UserSessionsInDB, UserInDB)
            .join(UserInDB)
            .where(UserSessionsInDB.user_id == user_id)
            .where(UserSessionsInDB.session_id == UUID(hex=session_id))
            .limit(1)
        )
        result = await session.execute(stmt)
        row = result.one_or_none()
        if row:
            user_session, user = row
            return user, user_session
        else:
            return None, None

    @staticmethod
    async def get_by_email(email: str, session: AsyncSession) -> UserInDB | None:
        stmt = select(UserInDB).where(UserInDB.email == email).limit(1)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(username: str, session: AsyncSession) -> UserInDB | None:
        stmt = select(UserInDB).where(UserInDB.username == username).limit(1)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_password(
        user: UserInDB, new_password: str, session: AsyncSession
    ) -> None:
        user.hashed_password = hash_password(new_password)
        session.add(user)
        await session.commit()

    @staticmethod
    async def verify_email(
        user: UserInDB,
        session: AsyncSession,
    ) -> None:
        user.email_verified = True
        session.add(user)
        await session.commit()
