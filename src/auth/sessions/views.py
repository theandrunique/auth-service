from fastapi import APIRouter

from src.auth.dependencies import UserAuthorization
from src.database import DbSession

from .crud import get_sessions_from_db_by_user_id
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
            jti=session.jti,
            created_at=session.created_at,
            last_accessed=session.last_accessed,
            ip_address=session.ip_address,
        )
        for session in sessions
    ]

    return UserSessions(
        user_sessions=session_schemas,
    )

