from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request, status

from src.auth.schemas import Token
from src.auth.utils import create_session
from src.emails.dependencies import OtpEmailDep, ResetPassEmailDep, VerifyEmailDep
from src.mongo.dependencies import MongoSession
from src.users.dependencies import UsersRepositoryDep
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
    repository: UsersRepositoryDep,
) -> None:
    user = await repository.get_by_email(email=email.email)
    if user and not user.email_verified:
        return worker.add_task(send_verify_email, user.email, user.username)


@router.post("/verify/", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(
    email: VerifyEmailDep,
    repository: UsersRepositoryDep,
) -> None:
    user = await repository.get_by_email(email=email)
    if not user or not user.active:
        return
    await repository.verify_email(id=user.id)


@router.post("/forgot/", status_code=status.HTTP_204_NO_CONTENT)
async def recover_password(
    data: EmailRequest,
    repository: UsersRepositoryDep,
    worker: BackgroundTasks,
) -> None:
    # TODO: dont return any errors
    user = await repository.get_by_email(email=data.email)
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
    repository: UsersRepositoryDep,
) -> Any:
    # TODO: refactor
    user = await repository.get_by_email(email=email)
    if not user:
        raise UserNotFound()
    elif not user.active:
        raise InactiveUser()
    await repository.update_password(id=user.id, new_password=data.password)
    return user


@router.put("/otp/")
async def send_opt(
    otp_data: EmailRequest,
    worker: BackgroundTasks,
    repository: UsersRepositoryDep,
) -> dict[str, Any]:
    user = await repository.get_by_email(email=otp_data.email)
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
    repository: UsersRepositoryDep,
    mongo_session: MongoSession,
) -> Token:
    user = await repository.get_by_email(email=email)
    if not user:
        raise UserNotFound()
    if not user.active:
        raise InactiveUser()

    return await create_session(session=mongo_session, user_id=user.id, req=req)
