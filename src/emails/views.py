from typing import Any

from fastapi import APIRouter, BackgroundTasks, status

from src.emails.dependencies import ResetPassEmailDep, VerifyEmailDep
from src.users.dependencies import UsersRepositoryDep
from src.users.exceptions import UserNotFound
from src.users.schemas import ResetPasswordSchema

from .exceptions import EmailNotVerified
from .schemas import EmailRequest
from .utils import (
    send_reset_password_email,
    send_verify_email,
)

router = APIRouter(tags=["emails"])


@router.post("/verification/request", status_code=status.HTTP_202_ACCEPTED)
async def send_confirmation_email(
    email: EmailRequest,
    worker: BackgroundTasks,
    repository: UsersRepositoryDep,
) -> None:
    user = await repository.get_by_email(email=email.email)
    if user and not user.email_verified:
        return worker.add_task(send_verify_email, user)


@router.post("/verification/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(
    user_id: VerifyEmailDep,
    repository: UsersRepositoryDep,
) -> None:
    user = await repository.get(user_id)
    if not user or not user.active:
        return
    await repository.verify_email(id=user.id)


@router.post("/password-recovery", status_code=status.HTTP_202_ACCEPTED)
async def recover_password(
    data: EmailRequest,
    repository: UsersRepositoryDep,
    worker: BackgroundTasks,
) -> None:
    user = await repository.get_by_email(email=data.email)
    if not user:
        raise UserNotFound()
    elif not user.email_verified:
        raise EmailNotVerified()
    worker.add_task(send_reset_password_email, user)


@router.post("/password-reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    data: ResetPasswordSchema,
    user_id: ResetPassEmailDep,
    repository: UsersRepositoryDep,
) -> Any:
    user = await repository.get(user_id)
    if not user:
        raise UserNotFound()
    await repository.update_password(id=user.id, new_password=data.password)
