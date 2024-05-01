from typing import Any
from uuid import UUID

from fastapi import APIRouter, status
from pydantic import NonNegativeInt

from src.auth.dependencies import UserAuthorizationWithSession

from .dependencies import SessionRepositoryDep
from .schemas import SessionSchema, UserSessions

router = APIRouter()


@router.get("/", response_model=UserSessions)
async def get_my_sessions(
    repository: SessionRepositoryDep,
    offset: NonNegativeInt = 0,
    count: NonNegativeInt = 20,
) -> UserSessions:
    user_sessions = await repository.get_many(count=count, offset=offset)
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
    repository: SessionRepositoryDep,
) -> None:
    _, user_session = user_with_session
    await repository.delete_except(except_id=user_session.id)


@router.delete("/{session_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    repository: SessionRepositoryDep,
    session_id: UUID,
) -> None:
    await repository.delete(id=session_id)


@router.delete("/logout-all/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_sessions(
    repository: SessionRepositoryDep,
) -> None:
    await repository.delete_all()
