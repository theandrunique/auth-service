from typing import Any
from uuid import UUID

from fastapi import APIRouter, status
from pydantic import NonNegativeInt

from src.auth.dependencies import UserAuthorizationWithSession

from .dependencies import SessionServiceDep
from .schemas import SessionSchema, UserSessions

router = APIRouter()


@router.get("/", response_model=UserSessions)
async def get_my_sessions(
    service: SessionServiceDep,
    offset: NonNegativeInt = 0,
    count: NonNegativeInt = 20,
) -> UserSessions:
    user_sessions = await service.get_many(count=count, offset=offset)
    return UserSessions(
        user_sessions=user_sessions,
    )


@router.get("/current/", response_model=SessionSchema)
async def get_current_session(
    user_with_session: UserAuthorizationWithSession,
) -> Any:
    _, user_session = user_with_session
    return user_session


@router.delete("/logout-others/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_sessions_except_current(
    user_with_session: UserAuthorizationWithSession,
    service: SessionServiceDep,
) -> None:
    _, user_session = user_with_session
    await service.delete_except(except_id=user_session.id)


@router.delete("/{session_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    service: SessionServiceDep,
    session_id: UUID,
) -> None:
    await service.delete(id=session_id)


@router.delete("/logout-all/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_sessions(
    service: SessionServiceDep,
) -> None:
    await service.delete_all()
