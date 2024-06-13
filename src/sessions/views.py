from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from pydantic import NonNegativeInt

from src.auth.dependencies import (
    UserAuthorization,
    UserAuthorizationWithSession,
    get_user,
)
from src.dependencies import Container, Provide

from .schemas import UserSessions

router = APIRouter(dependencies=[Depends(get_user)])


@router.get("", response_model=UserSessions)
async def get_sessions(
    user: UserAuthorization,
    offset: NonNegativeInt = 0,
    count: NonNegativeInt = 20,
    sessions_service=Provide(Container.SessionsService),
) -> UserSessions:
    user_sessions = await sessions_service.get_many(
        user_id=user.id, count=count, offset=offset
    )
    return UserSessions(
        user_sessions=user_sessions,
    )


@router.delete("/logout-others", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_sessions_except_current(
    user_with_session: UserAuthorizationWithSession,
    sessions_service=Provide(Container.SessionsService),
) -> None:
    _, user_session = user_with_session
    await sessions_service.delete_except(except_id=user_session.id)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    res: Response,
    sessions_service=Provide(Container.SessionsService),
) -> None:
    await sessions_service.delete(id=session_id, res=res)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_sessions(
    user: UserAuthorization,
    sessions_service=Provide(Container.SessionsService),
) -> None:
    await sessions_service.delete_all(user_id=user.id)
