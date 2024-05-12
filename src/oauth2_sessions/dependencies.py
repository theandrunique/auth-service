from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.auth.dependencies import UserAuthorization
from src.mongo import db

from .repository import OAuth2SessionsRepository
from .service import OAuth2SessionsService


def get_oauth2_sessions_service_by_id(user_id: UUID) -> OAuth2SessionsService:
    return OAuth2SessionsService(
        repository=OAuth2SessionsRepository(
            collection=db[f"oauth2_sessions_{user_id.hex}"],
        )
    )


async def get_oauth2_sessions_service(user: UserAuthorization) -> OAuth2SessionsService:
    return get_oauth2_sessions_service_by_id(user.id)


OAuth2SessionsServiceDep = Annotated[
    OAuth2SessionsService, Depends(get_oauth2_sessions_service)
]
