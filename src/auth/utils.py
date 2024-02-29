from typing import Annotated

from fastapi import Depends, Security, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from jwt.exceptions import PyJWTError

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from models import UserInDB
from db_helper import db_helper

from .schemas import TokenPayload, TokenType, UserSchema
from .crud import get_user_from_db_by_id, get_user_from_db_by_username
from .security import validate_password, validate_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={},
)


async def authenticate_user(
    username: str,
    password: str,
    session: AsyncSession,
) -> UserInDB:
    user: UserInDB = await get_user_from_db_by_username(username, session)

    if user is not None and validate_password(
        password=password,
        hashed_password=user.hashed_password,
    ):
        return user

    return None


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> UserInDB:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload: TokenPayload = validate_token(token=token, token_type=TokenType.ACCESS)
        if payload.sub is None:
            raise credentials_exception

    except (PyJWTError, ValidationError):
        raise credentials_exception

    user = await get_user_from_db_by_id(id=payload.sub, session=session)

    if user is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in payload.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


async def get_current_active_user(
    current_user: Annotated[UserInDB, Security(get_current_user)],
) -> UserInDB:
    if not current_user.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


def get_access_token(
    current_user: UserSchema = Security(get_current_active_user),
) -> UserSchema:
    return current_user
