import logging
from typing import Annotated, Any

import jwt
from config import settings
from db_helper import db_helper
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Security,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from jwt.exceptions import PyJWTError
from models import UserInDB
from redis_helper import redis_client
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import (
    create_new_refresh_token,
    create_new_user,
    get_refresh_token_from_db_by_id,
    get_user_from_db_by_email,
    revoke_refresh_token,
    update_refresh_token,
    update_user_password,
    update_user_verify_email,
)
from .email_utils import (
    EmailTokenType,
    send_otp_email,
    send_reset_password_email,
    send_verify_email,
    verify_email_token,
)
from .schemas import (
    AuthSchema,
    NewPasswordSchema,
    OtpAuthSchema,
    TokenPair,
    TokenPayload,
    TokenType,
    UserSchema,
)
from .security import (
    create_tokens,
    gen_key,
    gen_otp,
    gen_random_token_id,
    validate_token,
)
from .utils import (
    authenticate_user,
    get_access_token,
    oauth2_scheme,
)

router = APIRouter()


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserSchema,
)
async def register(
    auth_data: AuthSchema,
    session: AsyncSession = Depends(db_helper.session_dependency),
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists",
        )
    except Exception as e:
        logging.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/token/")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> TokenPair:
    user: UserInDB | None = await authenticate_user(
        username=form_data.username,
        password=form_data.password,
        session=session,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    jti = gen_random_token_id()
    refresh_token_in_db = await create_new_refresh_token(
        user_id=user.id,
        jti=jti,
        ip_address=request.client.host if request.client is not None else None,
        session=session,
    )
    payload = TokenPayload(
        sub=user.id,
        scopes=form_data.scopes,
        jti=jti,
        token_id=refresh_token_in_db.id,
    )

    tokens_pair = create_tokens(payload=payload)
    return tokens_pair


@router.get("/refresh-token/")
async def refresh_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    request: Request,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> TokenPair:
    try:
        payload = validate_token(token=token, token_type=TokenType.REFRESH)
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )
    prev_token = await get_refresh_token_from_db_by_id(
        token_id=payload.token_id,
        session=session,
    )
    if prev_token is not None and prev_token.jti == payload.jti:
        new_jti = gen_random_token_id()
        payload.jti = new_jti
        tokens_pair = create_tokens(payload=payload)
        await update_refresh_token(
            token=prev_token,
            new_token_id=new_jti,
            ip_address=request.client.host if request.client is not None else None,
            session=session,
        )
        return tokens_pair

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid token",
    )


@router.get("/introspect/")
def introspect_token(token: str = Depends(oauth2_scheme)) -> Any:
    try:
        payload = jwt.decode(
            jwt=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return payload


@router.get("/me/", response_model=UserSchema)
def get_me(user: UserInDB = Security(get_access_token, scopes=["me"])) -> Any:
    return user


@router.delete("/revoke-token/")
async def revoke_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> dict[str, str]:
    try:
        payload = validate_token(token=token, token_type=TokenType.REFRESH)
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )
    prev_token = await get_refresh_token_from_db_by_id(
        token_id=payload.token_id,
        session=session,
    )
    if prev_token is not None and prev_token.jti == payload.jti:
        await revoke_refresh_token(token=prev_token, session=session)
        return {"detail": "Token revoked successfully"}

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid token",
    )


@router.post("/password-recovery/{email}")
async def recover_password(
    email: str,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> dict[str, Any]:
    user = await get_user_from_db_by_email(email=email, session=session)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    elif not user.email_verified:
        raise HTTPException(status_code=400, detail="Email is not verified")
    send_reset_password_email(email_to=email)
    return {"message": "Password recovery email sent"}


@router.post("/reset-password/")
async def reset_password(
    body: NewPasswordSchema,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> dict[str, Any]:
    email = verify_email_token(token=body.token, type=EmailTokenType.RECOVERY_PASSWORD)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await get_user_from_db_by_email(email=email, session=session)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    await update_user_password(
        user=user,
        new_password=body.new_password,
        session=session,
    )
    return {"message": "Password updated successfully"}


@router.post("/send-confirmation-email/")
async def send_confirmation_email(
    user: UserInDB = Security(get_access_token),
) -> dict[str, Any]:
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The email address has already been verified",
        )
    send_verify_email(email_to=user.email, username=user.username)
    return {"message": "Verification email sent"}


@router.post("/verify-email/")
async def verify_email(
    token: str,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> dict[str, Any]:
    email = verify_email_token(token=token, type=EmailTokenType.VERIFY_EMAIL)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await get_user_from_db_by_email(email=email, session=session)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    await update_user_verify_email(user=user, session=session)
    return {"message": "Email verified successfully"}


@router.post("/otp-auth/")
async def otp_auth(
    otp_auth_data: OtpAuthSchema,
    request: Request,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> TokenPair:
    expected_value = await redis_client.hget(
        f"otp_user_{otp_auth_data.email}",
        key=otp_auth_data.key,
    )

    if expected_value != otp_auth_data.otp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP",
        )
    await redis_client.delete(f"otp_user_{otp_auth_data.email}")
    user = await get_user_from_db_by_email(email=otp_auth_data.email, session=session)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    jti = gen_random_token_id()
    refresh_token_in_db = await create_new_refresh_token(
        user_id=user.id,
        jti=jti,
        ip_address=request.client.host if request.client is not None else None,
        session=session,
    )
    payload = TokenPayload(
        sub=user.id,
        scopes=otp_auth_data.scopes,
        jti=jti,
        token_id=refresh_token_in_db.id,
    )

    tokens_pair = create_tokens(payload=payload)
    return tokens_pair


@router.get("/send-otp/")
async def send_opt(
    email: str,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> dict[str, str]:
    user = await get_user_from_db_by_email(email=email, session=session)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not user.email_verified:
        raise HTTPException(status_code=400, detail="Email is not verified")

    opt = gen_otp()
    key = gen_key()
    await redis_client.hset(f"otp_user_{user.email}", key, opt)
    await redis_client.expire(f"otp_user_{user.email}", settings.OTP_EXPIRE_SECONDS)
    send_otp_email(email_to=email, username=user.username, opt=opt)
    return {"message": "OPT sent on your email", "key": key}
