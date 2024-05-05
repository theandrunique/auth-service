from typing import Any

from fastapi import APIRouter, BackgroundTasks, status

from src.emails.dependencies import ResetPassEmailDep, VerifyEmailDep
from src.redis import RedisClient
from src.users.dependencies import UsersRepositoryDep
from src.users.exceptions import InactiveUser, UserNotFound
from src.users.schemas import ResetPasswordSchema, UserSchema

from .config import settings
from .exceptions import EmailNotVerified
from .schemas import EmailRequest, ResetPasswordTokenPayload, VerificationTokenPayload
from .utils import (
    send_reset_password_email,
    send_verify_email,
)

router = APIRouter(tags=["emails"])


@router.put("/verify/", status_code=status.HTTP_204_NO_CONTENT)
async def send_confirmation_email(
    email: EmailRequest,
    worker: BackgroundTasks,
    repository: UsersRepositoryDep,
    redis: RedisClient,
) -> None:
    user = await repository.get_by_email(email=email.email)
    if user and not user.email_verified:
        payload = VerificationTokenPayload(sub=user.id)
        await redis.set(
            f"verify_email_token_id_{user.email}",
            payload.jti.hex,
            ex=settings.VERIFICATION_TOKEN_EXPIRE_SECONDS,
        )
        return worker.add_task(send_verify_email, user.email, user.username, payload)


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
    redis: RedisClient,
) -> None:
    # TODO: dont return any errors
    user = await repository.get_by_email(email=data.email)
    if not user:
        raise UserNotFound()
    elif not user.active:
        raise InactiveUser()
    elif not user.email_verified:
        raise EmailNotVerified()
    payload = ResetPasswordTokenPayload(sub=user.id)
    await redis.set(
        f"reset_password_token_id_{data.email}",
        payload.jti.hex,
        ex=settings.RESET_TOKEN_EXPIRE_SECONDS,
    )
    worker.add_task(send_reset_password_email, data.email, payload)


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
