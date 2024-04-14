from fastapi import APIRouter, BackgroundTasks, status

from src.dependencies import DbSession
from src.emails.dependencies import VerifyEmailDep
from src.users.crud import UsersDB

from .schemas import EmailReq
from .utils import send_verify_email

router = APIRouter(tags=["emails"])


@router.put("/verify/", status_code=status.HTTP_204_NO_CONTENT)
async def send_confirmation_email(
    email: EmailReq,
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
