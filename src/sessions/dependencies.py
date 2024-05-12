from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.auth.dependencies import UserAuthorization
from src.mongo import db
from src.sessions.service import SessionsService

from .repository import SessionsRepository


def get_user_sessions_service(user: UserAuthorization) -> SessionsService:
    return get_user_sessions_service_by_id(user.id)


def get_user_sessions_service_by_id(user_id: UUID) -> SessionsService:
    return SessionsService(
        repository=SessionsRepository(
            collection=db[f"sessions_{user_id.hex}"],
        )
    )


SessionServiceDep = Annotated[SessionsService, Depends(get_user_sessions_service)]
