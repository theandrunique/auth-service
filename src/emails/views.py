from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request, status

from src.auth.schemas import Token
from src.auth.utils import create_new_session
from src.dependencies import DbSession
from src.emails.dependencies import OtpEmailDep, ResetPassEmailDep, VerifyEmailDep
from src.users.crud import UsersDB
from src.users.exceptions import InactiveUser, UserNotFound
from src.users.schemas import ResetPasswordSchema, UserSchema

from .exceptions import EmailNotVerified
from .schemas import EmailRequest
from .utils import (
    gen_otp_with_token,
    send_otp_email,
    send_reset_password_email,
    send_verify_email,
)

router = APIRouter(tags=["emails"])


@router.put("/verify/", status_code=status.HTTP_204_NO_CONTENT)
async def send_confirmation_email(
    email: EmailRequest,
    worker: BackgroundTasks,
    session: DbSession,
) -> None:
    user = await UsersDB.get_by_email(email=email.email, session=session)
    if user and not user.email_verified:
        return worker.add_task(send_verify_email, user.email, user.username)


@router.post("/verify/", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(
    email: VerifyEmailDep,
    session: DbSession,
) -> None:
    user = await UsersDB.get_by_email(email=email, session=session)
    if not user or not user.active:
        return
    await UsersDB.verify_email(user=user, session=session)


@router.post("/forgot/", status_code=status.HTTP_204_NO_CONTENT)
async def recover_password(
    data: EmailRequest,
    session: DbSession,
    worker: BackgroundTasks,
) -> None:
    # TODO: dont return any errors
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
) -> Token:
    user = await UsersDB.get_by_email(email=email, session=session)
    if not user:
        raise UserNotFound()
    if not user.active:
        raise InactiveUser()
    return await create_new_session(req=req, user=user, session=session)
