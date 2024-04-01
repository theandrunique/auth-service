from fastapi import APIRouter, BackgroundTasks, status

from src.dependencies import DbSession, UserAuthorization
from src.emails.dependencies import VerifyEmailDep
from src.users.crud import UsersDB
from src.users.exceptions import InactiveUser, UserNotFound

from .exceptions import EmailAlreadyVerified
from .utils import send_verify_email

router = APIRouter(tags=["emails"])


@router.put("/verify/", status_code=status.HTTP_204_NO_CONTENT)
async def send_confirmation_email(
    user: UserAuthorization,
    worker: BackgroundTasks,
) -> None:
    if user.email_verified:
        raise EmailAlreadyVerified()
    worker.add_task(send_verify_email, user.email, user.username)


@router.post("/verify/", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(
    email: VerifyEmailDep,
    session: DbSession,
) -> None:
    user = await UsersDB.get_by_email(email=email, session=session)
    if not user:
        raise UserNotFound()
    elif not user.active:
        raise InactiveUser()
    await UsersDB.verify_email(user=user, session=session)
