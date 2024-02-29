import logging
from typing import Annotated

from fastapi import (
    Depends,
    APIRouter,
    HTTPException,
    Security,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import jwt
from jwt.exceptions import PyJWTError
from models import UserInDB
from db_helper import db_helper

from .schemas import AuthSchema, TokenPayload, TokenType, UserSchema
from .crud import (
    create_new_refresh_token,
    create_new_user,
    get_refresh_token_from_db_by_id,
    update_refresh_token,
)
from .security import create_tokens, validate_token, gen_random_token_id
from .utils import (
    authenticate_user,
    get_access_token,
    oauth2_scheme,
)
from config import settings


router = APIRouter()


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserSchema,
)
async def register(
    auth_data: AuthSchema,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    try:
        new_user = await create_new_user(
            username=auth_data.username,
            password=auth_data.password,
            session=session,
        )
        return new_user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists",
        )
    except Exception as e:
        logging.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/token/")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(db_helper.session_dependency),
):
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
    session: AsyncSession = Depends(db_helper.session_dependency),
):
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
            session=session,
        )
        return tokens_pair

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid token",
    )


@router.get("/introspect/")
def introspect_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return payload


@router.get("/me/", response_model=UserSchema)
def get_me(user: UserInDB = Security(get_access_token, scopes=["me"])):
    return user
