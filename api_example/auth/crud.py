from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import UserInDB, RefreshTokenInDB
from .security import hash_password


async def create_new_user(
    username: str,
    password: str,
    session: AsyncSession,
):
    new_user = UserInDB(
        username=username,
        hashed_password=hash_password(password),
    )
    session.add(new_user)
    await session.commit()
    return new_user


async def get_user_from_db_by_username(
    username: str,
    session: AsyncSession
) -> UserInDB | None:
    stmt = select(UserInDB).where(UserInDB.username == username).limit(1)
    result: Result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_from_db_by_id(
    id: int,
    session: AsyncSession
) -> UserInDB | None:
    return await session.get(UserInDB, ident=id)


async def get_refresh_token_from_db(
    token: str, 
    user_id: str,
    session: AsyncSession,
) -> RefreshTokenInDB | None:
    stmt = (
        select(RefreshTokenInDB)
        .where(RefreshTokenInDB.user_id == user_id)
        .where(RefreshTokenInDB.token == token)
    )
    result: Result = await session.execute(stmt)
    return result.scalar_one_or_none()
