import datetime

from models import RefreshTokenInDB, UserInDB
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .security import hash_password


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


async def create_new_refresh_token(
    user_id: int,
    jti: str,
    ip_address: str | None,
    session: AsyncSession,
) -> RefreshTokenInDB:
    new_token = RefreshTokenInDB(
        user_id=user_id,
        jti=jti,
        created_at=datetime.datetime.now(),
        last_accessed=datetime.datetime.now(),
        ip_address=ip_address,
    )
    session.add(new_token)
    await session.commit()
    return new_token


async def update_refresh_token(
    token: RefreshTokenInDB,
    new_token_id: str,
    ip_address: str | None,
    session: AsyncSession,
) -> None:
    token.jti = new_token_id
    token.ip_address = ip_address
    token.last_accessed = datetime.datetime.now()
    session.add(token)
    await session.commit()


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


async def get_refresh_token_from_db_by_id(
    token_id: int,
    session: AsyncSession,
) -> RefreshTokenInDB | None:
    return await session.get(RefreshTokenInDB, ident=token_id)


async def revoke_refresh_token(
    token: RefreshTokenInDB,
    session: AsyncSession,
) -> None:
    await session.delete(token)
    await session.commit()
