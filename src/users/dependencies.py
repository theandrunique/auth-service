from typing import Annotated

from fastapi import Depends

from src.mongo import MongoSession

from .repository import UsersRepository


async def get_users_repository(session: MongoSession) -> UsersRepository:
    return UsersRepository(session=session)


UsersRepositoryDep = Annotated[UsersRepository, Depends(get_users_repository)]
