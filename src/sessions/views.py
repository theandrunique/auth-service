from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from pydantic import NonNegativeInt

from src.auth.dependencies import (
    UserAuthorization,
    UserAuthorizationWithSession,
    get_user,
)

from .dependencies import SessionServiceDep
from .schemas import UserSessions

router = APIRouter(dependencies=[Depends(get_user)])


@router.get("", response_model=UserSessions)
async def get_sessions(
    service: SessionServiceDep,
    user: UserAuthorization,
    offset: NonNegativeInt = 0,
    count: NonNegativeInt = 20,
) -> UserSessions:
    user_sessions = await service.get_many(user_id=user.id, count=count, offset=offset)
    return UserSessions(
        user_sessions=user_sessions,
    )


@router.delete("/logout-others", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_sessions_except_current(
    user_with_session: UserAuthorizationWithSession,
    service: SessionServiceDep,
) -> None:
    _, user_session = user_with_session
    await service.delete_except(except_id=user_session.id)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    service: SessionServiceDep,
    session_id: UUID,
    res: Response,
) -> None:
    await service.delete(id=session_id, res=res)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_sessions(
    service: SessionServiceDep,
    user: UserAuthorization,
) -> None:
    await service.delete_all(user_id=user.id)
