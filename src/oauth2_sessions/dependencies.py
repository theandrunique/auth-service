from typing import Annotated

from fastapi import Depends

from src.auth.dependencies import UserAuthorization
from src.mongo import MongoSession

from .repository import OAuth2SessionsRepository


async def get_oauth2_sessions_repository(
    session: MongoSession, user: UserAuthorization
) -> OAuth2SessionsRepository:
    return OAuth2SessionsRepository(session=session, user_id=user.id)


OAuth2SessionsRepositoryDep = Annotated[
    OAuth2SessionsRepository, Depends(get_oauth2_sessions_repository)
]
