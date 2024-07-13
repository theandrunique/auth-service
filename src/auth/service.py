from dataclasses import dataclass
from uuid import UUID

from src.auth.exceptions import InactiveUser, InvalidSession
from src.services.hash import Hash
from src.services.jwe import JWE
from src.sessions.entities import Session
from src.sessions.service import ISessionsService
from src.users.entities import User
from src.users.service import IUsersService


class IAuthService:
    async def validate_session(self, session_token: str) -> tuple[User, Session]: ...


@dataclass
class AuthService(IAuthService):
    users_service: IUsersService
    sessions_service: ISessionsService
    hash_service: Hash
    jwe: JWE

    async def validate_session(self, session_token: str) -> tuple[User, Session]:
        session_id_bytes = self.jwe.decode(session_token)
        if session_id_bytes is None:
            raise InvalidSession

        try:
            session_id = UUID(bytes=session_id_bytes)
        except Exception:
            raise InvalidSession

        session = await self.sessions_service.get_by_id(session_id)
        if session is None:
            raise InvalidSession

        user = await self.users_service.get_by_id(session.user_id)
        if not user:
            raise InvalidSession

        if not user.active:
            raise InactiveUser

        await self.sessions_service.update_last_used(session_id)

        return user, session
