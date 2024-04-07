import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from src.dependencies import DbSession, UserAuthorization, UserAuthorizationWithSession

from .crud import SessionsDB
from .schemas import SessionSchema, UserSessions

router = APIRouter()


@router.get("/", response_model=UserSessions)
async def get_my_sessions(
    user: UserAuthorization,
    session: DbSession,
) -> UserSessions:
    user_sessions = await SessionsDB.get_by_user_id(
        user_id=user.id,
        session=session,
    )
    time_now = datetime.datetime.now()

    expired_ids = [
        user_session.session_id
        for user_session in user_sessions
        if user_session.expires_at < time_now
    ]
    if expired_ids:
        await SessionsDB.revoke_by_ids(
            user_id=user.id,
            session_ids=expired_ids,
            session=session,
        )
    session_schemas = [
        SessionSchema(
            session_id=user_session.session_id,
            last_used=user_session.last_used,
            ip_address=user_session.ip_address,
            expires_at=user_session.expires_at,
        )
        for user_session in user_sessions
        if user_session.expires_at >= time_now
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
    await SessionsDB.revoke_except(
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
    await SessionsDB.revoke_by_id(
        user_id=user.id,
        session_id=session_id,
        session=session,
    )
