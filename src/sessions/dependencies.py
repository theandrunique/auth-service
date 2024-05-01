from typing import Annotated

from fastapi import Depends

from src.auth.dependencies import UserAuthorization
from src.mongo import MongoSession

from .repository import SessionsRepository


async def get_users_repository(
    session: MongoSession, user: UserAuthorization
) -> SessionsRepository:
    repository = SessionsRepository(session=session, user_id=user.id)
    await repository.delete_expired_sessions()
    return repository


SessionRepositoryDep = Annotated[SessionsRepository, Depends(get_users_repository)]
