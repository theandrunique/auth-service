import datetime
import logging
from typing import Annotated

from fastapi import (
    Depends,
    APIRouter,
    HTTPException,
    Security,
    status,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import jwt
from jwt.exceptions import PyJWTError
from models import RefreshTokenInDB, UserInDB
from db_helper import db_helper

from .schemas import AuthSchema, UserSchema
from .crud import create_new_user, get_refresh_token_from_db
from .security import (
    create_token,
    validate_token,
)
from .utils import (
    authenticate_user,
    get_access_token,
    oauth2_scheme,
)
from config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM,
)


router = APIRouter()


@router.post("/register/", status_code=status.HTTP_201_CREATED)
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
        return {
            "status": "ok",
        }
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


@router.post("/auth/")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    user: UserInDB = await authenticate_user(
        username=form_data.username,
        password=form_data.password,
        session=session,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    refresh_token = create_token(
        data={
            "sub": user.id,
            "scopes": form_data.scopes,
        },
        expires_delta=datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
        token_type="refresh",
    )
    
    access_token = create_token(
        data={
            "sub": user.id,
            "scopes": form_data.scopes,
        },
        expires_delta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )
    new_refresh_token = RefreshTokenInDB(user_id=user.id, token=refresh_token)
    session.add(new_refresh_token)
    await session.commit()
    return {
        "refresh_token": refresh_token,
        "access_token": access_token,
    }


@router.get("/refresh-token/")
async def refresh(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    try:
        payload = validate_token(token=token, token_type="refresh")
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )
    prev_token = await get_refresh_token_from_db(
        user_id=payload["sub"],
        token=token,
        session=session,
    )
    if prev_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )
    access_token = create_token(
        data={
            "sub": payload["sub"],
            "scopes": payload["scopes"],
        },
        expires_delta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )

    refresh_token = create_token(
        data={
            "sub": payload["sub"],
            "scopes": payload["scopes"],
        },
        expires_delta=datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
        token_type="refresh",
    )
    prev_token.token = refresh_token
    session.add(prev_token)
    await session.commit()

    return {
        "refresh_token": refresh_token,
        "access_token": access_token,
    }


@router.get("/introspect/")
def introspect_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            jwt=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    return payload

@router.get("/me/", response_model=UserSchema)
def refresh(user: UserInDB = Security(get_access_token)):
    return user
