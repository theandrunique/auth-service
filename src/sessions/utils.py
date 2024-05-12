from uuid import UUID

from src.mongo import db
from src.sessions.repository import SessionsRepository
from src.sessions.service import SessionsService


def get_user_sessions_service_by_id(user_id: UUID) -> SessionsService:
    return SessionsService(
        repository=SessionsRepository(
            collection=db[f"sessions_{user_id.hex}"],
        )
    )
