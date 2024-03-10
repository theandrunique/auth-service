import datetime
from uuid import UUID

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import UserInDB

from .models import UserSessionsInDB


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(
        password=password.encode(),
        salt=bcrypt.gensalt(),
    )


async def create_new_user(
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


async def create_new_user_session(
    user_id: int,
    session_id: UUID,
    ip_address: str | None,
    session: AsyncSession,
) -> UserSessionsInDB:
    new_session = UserSessionsInDB(
        user_id=user_id,
        session_id=session_id,
        last_used=datetime.datetime.now(),
        ip_address=ip_address,
    )
    session.add(new_session)
    await session.commit()
    return new_session


async def update_user_password(
    user: UserInDB, new_password: str, session: AsyncSession
) -> None:
    user.hashed_password = hash_password(new_password)
    session.add(user)
    await session.commit()


async def update_user_verify_email(
    user: UserInDB,
    session: AsyncSession,
) -> None:
    user.email_verified = True
    session.add(user)
    await session.commit()


async def get_user_from_db_by_username(
    username: str, session: AsyncSession
) -> UserInDB | None:
    stmt = select(UserInDB).where(UserInDB.username == username).limit(1)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_from_db_by_email(
    email: str, session: AsyncSession
) -> UserInDB | None:
    stmt = select(UserInDB).where(UserInDB.email == email).limit(1)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_from_db_by_id(id: int, session: AsyncSession) -> UserInDB | None:
    return await session.get(UserInDB, ident=id)


async def get_user_session_from_db(
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


async def get_user_with_session_from_db(
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
        return None
