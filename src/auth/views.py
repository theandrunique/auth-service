from typing import Any

from fastapi import (
    APIRouter,
    Request,
    Response,
    status,
)

from src.auth.use_cases import LoginCommand, LoginUseCase, LogoutCommand, LogoutUseCase, SignUpCommand, SignUpUseCase
from src.dependencies import Provide
from src.sessions.utils import delete_session_cookie, set_session_cookie
from src.users.schemas import UserSchema

from .dependencies import UserAuthorizationWithSession
from .schemas import LoginReq, RegistrationSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/sign-up",
    status_code=status.HTTP_201_CREATED,
    response_model=UserSchema,
)
async def register(
    data: RegistrationSchema,
    use_case=Provide(SignUpUseCase),
) -> Any:
    return await use_case.execute(
        SignUpCommand(
            username=data.username,
            email=data.email,
            password=data.password,
        )
    )


@router.post("/login")
async def login(
    data: LoginReq,
    res: Response,
    req: Request,
    use_case=Provide(LoginUseCase),
) -> None:
    assert req.client
    session_token = await use_case.execute(
        LoginCommand(
            login=data.login,
            password=data.password,
            ip_address=req.client.host,
        )
    )
    set_session_cookie(session_token, res=res)


@router.delete("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_token(
    user_with_session: UserAuthorizationWithSession,
    res: Response,
    use_case=Provide(LogoutUseCase),
) -> None:
    user, user_session = user_with_session
    await use_case.execute(LogoutCommand(user, session=user_session))
    delete_session_cookie(res=res)
