from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    Request,
    status,
)
from jwt.exceptions import PyJWTError
from sqlalchemy.exc import IntegrityError

from src.config import settings
from src.database import DbSession
from src.redis_helper import redis_client

from .crud import (
    create_new_refresh_token,
    create_new_user,
    get_refresh_token_from_db_by_id,
    get_user_from_db_by_email,
    get_user_from_db_by_id,
    get_user_from_db_by_username,
    revoke_refresh_token,
    update_refresh_token,
    update_user_password,
    update_user_verify_email,
)
from .dependencies import UserAuthorization, get_authorization
from .email_utils import (
    EmailTokenType,
    send_otp_email,
    send_reset_password_email,
    send_verify_email,
    verify_email_token,
)
from .exceptions import (
    EmailAlreadyVerified,
    EmailNotVerified,
    InactiveUser,
    InvalidCredentials,
    InvalidOtp,
    InvalidToken,
    UsernameOrEmailAlreadyExists,
    UserNotFound,
)
from .schemas import (
    ForgotPasswordSchema,
    OtpAuthSchema,
    OtpRequestSchema,
    RefreshToken,
    RegistrationSchema,
    ResetPasswordSchema,
    UserAccessTokenPayload,
    UserLoginSchema,
    UserRefreshTokenPayload,
    UserSchema,
    UserTokenPair,
    VerifyEmailSchema,
)
from .sessions.views import router as sessions_router
from .utils import (
    check_password,
    create_tokens,
    gen_otp,
    gen_random_token_id,
    validate_refresh_token,
)

router = APIRouter()
router.include_router(sessions_router, prefix="/sessions", tags=["sessions"])


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserSchema,
)
async def register(
    auth_data: RegistrationSchema,
    session: DbSession,
) -> Any:
    try:
        new_user = await create_new_user(
            username=auth_data.username,
            password=auth_data.password,
            email=auth_data.email,
            session=session,
        )
        return new_user
    except IntegrityError:
        raise UsernameOrEmailAlreadyExists()


@router.post("/login/")
async def login(
    user_data: UserLoginSchema,
    request: Request,
    session: DbSession,
) -> UserTokenPair:
    if "@" in user_data.login:
        user = await get_user_from_db_by_email(email=user_data.login, session=session)
    else:
        user = await get_user_from_db_by_username(
            username=user_data.login, session=session,
        )
    if user is None:
        raise UserNotFound()
    elif not check_password(
        password=user_data.password,
        hashed_password=user.hashed_password,
    ):
        raise InvalidCredentials()

    jti = gen_random_token_id()
    refresh_token_in_db = await create_new_refresh_token(
        user_id=user.id,
        jti=jti,
        address=request.client,
        session=session,
    )
    tokens_pair = create_tokens(
        access_payload=UserAccessTokenPayload(
            email=user.email,
            id=user.id,
        ),
        refresh_payload=UserRefreshTokenPayload(
            jti=refresh_token_in_db.jti,
            token_id=refresh_token_in_db.id,
        ),
    )
    return tokens_pair


@router.get("/refresh/")
async def refresh_token(
    token_data: RefreshToken,
    request: Request,
    session: DbSession,
) -> UserTokenPair:
    try:
        refresh_payload = validate_refresh_token(token=token_data.refresh_token)
    except PyJWTError:
        raise InvalidToken()
    prev_token = await get_refresh_token_from_db_by_id(
        token_id=refresh_payload.token_id,
        session=session,
    )
    if prev_token is None or prev_token.jti != refresh_payload.jti:
        raise InvalidToken()
    user = await get_user_from_db_by_id(id=prev_token.user_id, session=session)
    if not user:
        raise UserNotFound()
    if not user.active:
        raise InactiveUser()
    new_jti = gen_random_token_id()
    refresh_payload.jti = new_jti
    tokens_pair = create_tokens(
        access_payload=UserAccessTokenPayload(
            id=user.id,
            email=user.email,
        ),
        refresh_payload=refresh_payload,
    )
    await update_refresh_token(
        token=prev_token,
        new_token_id=new_jti,
        ip_address=request.client.host if request.client is not None else None,
        session=session,
    )
    return tokens_pair


@router.get("/me/", response_model=UserSchema)
def get_me(user: UserAuthorization) -> Any:
    return user


@router.delete("/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_token(
    session: DbSession,
    token: str = Depends(get_authorization),
) -> None:
    try:
        payload = validate_refresh_token(token=token)
    except PyJWTError:
        raise InvalidToken()
    prev_token = await get_refresh_token_from_db_by_id(
        token_id=payload.token_id,
        session=session,
    )
    if not prev_token or prev_token.jti != payload.jti:
        raise InvalidToken()
    await revoke_refresh_token(token=prev_token, session=session)


@router.post("/forgot/", status_code=status.HTTP_204_NO_CONTENT)
async def recover_password(
    data: ForgotPasswordSchema,
    session: DbSession,
) -> None:
    user = await get_user_from_db_by_email(email=data.email, session=session)
    if not user:
        UserNotFound()
    elif not user.email_verified:
        raise EmailNotVerified()
    send_reset_password_email(email_to=data.email)


@router.post("/reset/", response_model=UserSchema)
async def reset_password(
    data: ResetPasswordSchema,
    session: DbSession,
) -> Any:
    email = verify_email_token(token=data.token, type=EmailTokenType.RECOVERY_PASSWORD)
    if not email:
        raise InvalidToken()
    user = await get_user_from_db_by_email(email=email, session=session)
    if not user:
        raise UserNotFound()
    elif not user.active:
        raise InactiveUser()
    await update_user_password(
        user=user,
        new_password=data.password,
        session=session,
    )
    return user


@router.put("/verify/", status_code=status.HTTP_204_NO_CONTENT)
async def send_confirmation_email(
    user: UserAuthorization,
) -> None:
    if user.email_verified:
        raise EmailAlreadyVerified()
    send_verify_email(email_to=user.email, username=user.username)


@router.post("/verify/", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(
    data: VerifyEmailSchema,
    session: DbSession,
) -> None:
    email = verify_email_token(token=data.token, type=EmailTokenType.VERIFY_EMAIL)
    if not email:
        raise InvalidToken()
    user = await get_user_from_db_by_email(email=email, session=session)
    if not user:
        raise UserNotFound()
    elif not user.active:
        raise InactiveUser()
    await update_user_verify_email(user=user, session=session)


@router.put("/otp/", status_code=status.HTTP_204_NO_CONTENT)
async def send_opt(otp_data: OtpRequestSchema, session: DbSession) -> None:
    user = await get_user_from_db_by_email(email=otp_data.email, session=session)
    if not user:
        raise UserNotFound()
    elif not user.email_verified:
        raise EmailNotVerified()
    opt = gen_otp()
    await redis_client.set(
        f"otp_user_{user.email}",
        opt,
        ex=settings.OTP_EXPIRE_SECONDS,
    )
    send_otp_email(email_to=otp_data.email, username=user.username, opt=opt)


@router.post("/otp/")
async def otp_auth(
    otp_data: OtpAuthSchema, request: Request, session: DbSession,
) -> UserTokenPair:
    expected_value = await redis_client.get(f"otp_user_{otp_data.email}")
    if expected_value != otp_data.otp:
        raise InvalidOtp()
    await redis_client.delete(f"otp_user_{otp_data.email}")

    user = await get_user_from_db_by_email(email=otp_data.email, session=session)
    if not user:
        raise UserNotFound()
    if not user.active:
        raise InactiveUser()
    jti = gen_random_token_id()
    refresh_token_in_db = await create_new_refresh_token(
        user_id=user.id,
        jti=jti,
        address=request.client,
        session=session,
    )
    tokens_pair = create_tokens(
        access_payload=UserAccessTokenPayload(
            email=user.email,
            id=user.id,
        ),
        refresh_payload=UserRefreshTokenPayload(
            jti=refresh_token_in_db.jti,
            token_id=refresh_token_in_db.id,
        ),
    )
    return tokens_pair

