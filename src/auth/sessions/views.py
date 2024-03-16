from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from src.auth.dependencies import UserAuthorization, UserAuthorizationWithSession
from src.database import DbSession

from .crud import (
    get_sessions_from_db_by_user_id,
    revoke_user_sessions_by_id,
    revoke_user_sessions_except_current,
)
from .schemas import SessionSchema, UserSessions

router = APIRouter()


@router.get("/", response_model=UserSessions)
async def get_my_sessions(
    user: UserAuthorization,
    session: DbSession,
) -> UserSessions:
    sessions = await get_sessions_from_db_by_user_id(
        user_id=user.id,
        session=session,
    )
    session_schemas = [
        SessionSchema(
            session_id=session.session_id,
            last_used=session.last_used,
            ip_address=session.ip_address,
        )
        for session in sessions
    ]
    return UserSessions(
        user_sessions=session_schemas,
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
    session: DbSession,
) -> None:
    user, user_session = user_with_session
    await revoke_user_sessions_except_current(
        user_id=user.id,
        except_id=user_session.session_id,
        session=session,
    )


@router.delete("/{session_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    user: UserAuthorization,
    session: DbSession,
    session_id: UUID,
) -> None:
    await revoke_user_sessions_by_id(
        user_id=user.id,
        session_id=session_id,
        session=session,
    )
