from typing import Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Request,
    status,
)
from sqlalchemy.exc import IntegrityError

from src.dependencies import DbSession, UserAuthorizationWithSession
from src.emails.dependencies import OtpEmailDep, ResetPassEmailDep
from src.emails.utils import send_otp_email, send_reset_password_email
from src.sessions.crud import SessionsDB
from src.users.crud import UsersDB
from src.users.exceptions import (
    InactiveUser,
    UserNotFound,
)
from src.users.schemas import (
    RegistrationSchema,
    ResetPasswordSchema,
    UserSchema,
)

from .exceptions import (
    EmailNotVerified,
    InvalidCredentials,
    UsernameOrEmailAlreadyExists,
)
from .schemas import (
    EmailRequest,
    LoginSchema,
    UserTokenSchema,
)
from .utils import (
    check_password,
    create_new_session,
    gen_otp_with_token,
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
    try:
        new_user = await UsersDB.create_new(
            username=data.username,
            password=data.password,
            email=data.email,
            session=session,
        )
        return new_user
    except IntegrityError:
        raise UsernameOrEmailAlreadyExists()


@router.post("/login/")
async def login(
    data: LoginSchema,
    req: Request,
    session: DbSession,
) -> UserTokenSchema:
    if "@" in data.login:
        user = await UsersDB.get_by_email(email=data.login, session=session)
    else:
        user = await UsersDB.get_by_username(username=data.login, session=session)
    if user is None:
        raise UserNotFound()
    elif not user.active:
        raise InactiveUser()
    elif not check_password(
        password=data.password,
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


@router.post("/forgot/", status_code=status.HTTP_204_NO_CONTENT)
async def recover_password(
    data: EmailRequest,
    session: DbSession,
    worker: BackgroundTasks,
) -> None:
    user = await UsersDB.get_by_email(email=data.email, session=session)
    if not user:
        raise UserNotFound()
    elif not user.active:
        raise InactiveUser()
    elif not user.email_verified:
        raise EmailNotVerified()
    worker.add_task(send_reset_password_email, data.email)


@router.post("/reset/", response_model=UserSchema)
async def reset_password(
    data: ResetPasswordSchema,
    email: ResetPassEmailDep,
    session: DbSession,
) -> Any:
    # TODO: refactor
    user = await UsersDB.get_by_email(email=email, session=session)
    if not user:
        raise UserNotFound()
    elif not user.active:
        raise InactiveUser()
    await UsersDB.update_password(
        user=user,
        new_password=data.password,
        session=session,
    )
    return user


@router.put("/otp/")
async def send_opt(
    otp_data: EmailRequest, session: DbSession, worker: BackgroundTasks
) -> dict[str, Any]:
    user = await UsersDB.get_by_email(email=otp_data.email, session=session)
    if not user:
        raise UserNotFound()
    elif not user.email_verified:
        raise EmailNotVerified()
    otp, token = gen_otp_with_token()
    worker.add_task(send_otp_email, otp_data.email, user.username, otp, token)
    return {
        "token": token,
    }


@router.post("/otp/")
async def otp_auth(
    email: OtpEmailDep,
    req: Request,
    session: DbSession,
) -> UserTokenSchema:
    user = await UsersDB.get_by_email(email=email, session=session)
    if not user:
        raise UserNotFound()
    if not user.active:
        raise InactiveUser()
    return await create_new_session(req=req, user=user, session=session)
