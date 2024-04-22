from typing import Any

from fastapi import (
    APIRouter,
    Request,
    status,
)

from src.dependencies import DbSession, UserAuthorizationWithSession
from src.sessions.crud import SessionsDB
from src.users.crud import UsersDB
from src.users.schemas import (
    RegistrationSchema,
    UserSchema,
)

from .exceptions import (
    EmailAlreadyExists,
    InvalidCredentials,
    UsernameAlreadyExists,
)
from .schemas import (
    Login,
    UserToken,
)
from .utils import (
    check_password,
    create_new_session,
)

router = APIRouter()


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserSchema,
)
async def register(
    data: RegistrationSchema,
    session: DbSession,
) -> Any:
    existed_email = await UsersDB.get_by_email(email=data.email, session=session)
    if existed_email:
        raise EmailAlreadyExists()
    existed_username = await UsersDB.get_by_username(
        username=data.username, session=session
    )
    if existed_username:
        raise UsernameAlreadyExists()

    new_user = await UsersDB.create_new(
        username=data.username,
        password=data.password,
        email=data.email,
        session=session,
    )
    return new_user


@router.post("/login/")
async def login(
    login: Login,
    req: Request,
    session: DbSession,
) -> UserToken:
    if "@" in login.login:
        user = await UsersDB.get_by_email(email=login.login, session=session)
    else:
        user = await UsersDB.get_by_username(username=login.login, session=session)
    if user is None:
        raise InvalidCredentials()
    elif not user.active:
        raise InvalidCredentials()
    elif not check_password(
        password=login.password,
        hashed_password=user.hashed_password,
    ):
        raise InvalidCredentials()
    return await create_new_session(req=req, user=user, session=session)


@router.delete("/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_token(
    session: DbSession,
    user_with_session: UserAuthorizationWithSession,
) -> None:
    _, user_session = user_with_session
    await SessionsDB.revoke(
        user_session=user_session,
        session=session,
    )

