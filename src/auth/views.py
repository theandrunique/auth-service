from typing import Any

from fastapi import (
    APIRouter,
    Request,
    status,
)

from src import hash
from src.auth.dependencies import UserAuthorizationWithSession
from src.sessions.dependencies import SessionServiceDep
from src.users.dependencies import UsersServiceDep
from src.users.schemas import (
    RegistrationSchema,
    UserSchema,
)

from .exceptions import (
    EmailAlreadyExists,
    InvalidCredentials,
    UsernameAlreadyExists,
)
from .schemas import Login, Token
from .utils import create_session

router = APIRouter()


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserSchema,
)
async def register(
    data: RegistrationSchema,
    service: UsersServiceDep,
) -> Any:
    existed_email = await service.get_by_email(email=data.email)
    if existed_email:
        raise EmailAlreadyExists()
    existed_username = await service.get_by_username(username=data.username)
    if existed_username:
        raise UsernameAlreadyExists()

    new_user = await service.add(data)
    return new_user


@router.post("/login/")
async def login(
    login: Login,
    req: Request,
    service: UsersServiceDep,
) -> Token:
    if "@" in login.login:
        user = await service.get_by_email(email=login.login)
    else:
        user = await service.get_by_username(username=login.login)
    if user is None:
        raise InvalidCredentials()
    elif not user.active:
        raise InvalidCredentials()
    elif not hash.check(
        value=login.password,
        hashed_value=user.hashed_password,
    ):
        raise InvalidCredentials()
    return await create_session(user_id=user.id, req=req)


@router.delete("/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_token(
    user_with_session: UserAuthorizationWithSession,
    service: SessionServiceDep,
) -> None:
    _, user_session = user_with_session
    await service.delete(id=user_session.id)
