from typing import Annotated

from fastapi import Depends

from src.auth.dependencies import UserAuthorization

from .service import SessionsService, sessions_service_factory


def get_user_sessions_service(user: UserAuthorization) -> SessionsService:
    return sessions_service_factory(user.id)


SessionServiceDep = Annotated[SessionsService, Depends(get_user_sessions_service)]
