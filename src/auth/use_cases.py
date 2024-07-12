from dataclasses import dataclass

from src.auth.exceptions import InvalidCredentials
from src.exceptions import FieldError, FieldErrorCode, ServiceError, ServiceErrorCode
from src.services.base.hash import Hash
from src.services.base.jwe import JWE
from src.sessions.dto import CreateSessionDTO
from src.sessions.entities import Session
from src.sessions.service import ISessionsService
from src.users.dto import CreateUserDTO
from src.users.entities import User
from src.users.service import IUsersService


@dataclass
class SignUpCommand:
    username: str
    email: str
    password: str


@dataclass
class SignUpUseCase:
    users_service: IUsersService

    async def execute(self, command: SignUpCommand) -> User:
        errors: dict[str, FieldError] = {}

        if await self.users_service.get_by_username(command.username):
            errors["username"] = FieldError(code=FieldErrorCode.USERNAME_ALREADY_TAKEN)

        if await self.users_service.get_by_email(command.email):
            errors["email"] = FieldError(code=FieldErrorCode.EMAIL_ALREADY_REGISTERED)

        if errors:
            raise ServiceError(code=ServiceErrorCode.INVALID_FORM_BODY, errors=errors)

        return await self.users_service.register_new_user(
            CreateUserDTO(
                username=command.username,
                email=command.email,
                password=command.password,
            )
        )


@dataclass
class LoginCommand:
    login: str
    password: str
    ip_address: str


@dataclass
class LoginUseCase:
    users_service: IUsersService
    sessions_service: ISessionsService
    hash_service: Hash
    jwe: JWE

    async def execute(self, command: LoginCommand) -> str:
        if "@" in command.login:
            user = await self.users_service.get_by_email(email=command.login)
        else:
            user = await self.users_service.get_by_username(username=command.login)

        if user is None:
            raise InvalidCredentials

        elif not user.active:
            raise ServiceError(code=ServiceErrorCode.INACTIVE_USER)

        elif not self.hash_service.check(
            value=command.password,
            hashed_value=user.hashed_password,
        ):
            raise InvalidCredentials

        assert user.id
        session = await self.sessions_service.create_new_session(
            CreateSessionDTO(
                user_id=user.id,
                ip_address=command.ip_address,
            )
        )
        assert session.id
        session_token = self.jwe.encode(session.id.bytes)
        return session_token


@dataclass
class LogoutCommand:
    user: User
    session: Session


@dataclass
class LogoutUseCase:
    sessions_service: ISessionsService

    async def execute(self, command: LogoutCommand) -> None:
        assert command.session.id
        await self.sessions_service.delete(command.session.id)
