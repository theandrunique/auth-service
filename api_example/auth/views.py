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

from .schemas import AuthSchema, TokenType, UserSchema
from .crud import (
    create_new_refresh_token_field,
    create_new_user,
    get_refresh_token_from_db_by_id,
    update_refresh_token,
)
from .security import create_tokens, validate_token
from .utils import (
    authenticate_user,
    get_access_token,
    oauth2_scheme,
)
from config import SECRET_KEY, ALGORITHM


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
    refresh_token_in_db = await create_new_refresh_token_field(user_id=user.id, session=session) 
    tokens_pair = create_tokens({"sub": user.id, "scopes": form_data.scopes, "token_type": refresh_token_in_db.id})
    update_refresh_token(refresh_token_in_db, new_value=tokens_pair.refresh_token, session=session)
    return tokens_pair


@router.get("/refresh-token/")
async def refresh(
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
        token_id=payload["token_id"],
        session=session,
    )
    if prev_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )
    tokens_pair = create_tokens(data=payload)
    await update_refresh_token(
        token=prev_token,
        new_value=tokens_pair.refresh_token,
        session=session,
    )
    return tokens_pair


@router.get("/introspect/")
def introspect_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return payload

@router.get("/me/", response_model=UserSchema)
def refresh(user: UserInDB = Security(get_access_token)):
    return user
