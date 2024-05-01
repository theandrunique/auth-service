from typing import Any

from fastapi import (
    APIRouter,
    Request,
    status,
)

from src.dependencies import UserAuthorizationWithSession
from src.mongo.dependencies import MongoSession
from src.sessions.dependencies import SessionRepositoryDep
from src.users.dependencies import UsersRepositoryDep
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
    Token,
)
from .utils import (
    check_password,
    create_session,
)

router = APIRouter()


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserSchema,
)
async def register(
    data: RegistrationSchema,
    repository: UsersRepositoryDep,
) -> Any:
    existed_email = await repository.get_by_email(email=data.email)
    if existed_email:
        raise EmailAlreadyExists()
    existed_username = await repository.get_by_username(username=data.username)
    if existed_username:
        raise UsernameAlreadyExists()

    new_user = await repository.add(data)
    return new_user


@router.post("/login/")
async def login(
    login: Login,
    req: Request,
    repository: UsersRepositoryDep,
    mongo_session: MongoSession,
) -> Token:
    if "@" in login.login:
        user = await repository.get_by_email(email=login.login)
    else:
        user = await repository.get_by_username(username=login.login)
    if user is None:
        raise InvalidCredentials()
    elif not user.active:
        raise InvalidCredentials()
    elif not check_password(
        password=login.password,
        hashed_password=user.hashed_password,
    ):
        raise InvalidCredentials()
    return await create_session(session=mongo_session, user_id=user.id, req=req)


@router.delete("/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_token(
    user_with_session: UserAuthorizationWithSession,
    repository: SessionRepositoryDep,
) -> None:
    _, user_session = user_with_session
    await repository.delete(id=user_session.id)
