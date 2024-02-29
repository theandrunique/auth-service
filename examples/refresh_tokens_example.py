import datetime
from collections import defaultdict
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jwt.exceptions import PyJWTError
from pydantic import BaseModel, ValidationError

app = FastAPI()


SECRET_KEY = "381fe4a2683cd0eee27cd66bfe1e5b02142ab7ee64d4f1ccbf1011e7358b005e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
REFRESH_TOKEN_EXPIRE_MINUTES = 24 * 60


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth",
    scopes={},
)


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(
        password=password.encode(),
        salt=bcrypt.gensalt(),
    )


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": hash_password("12345"),
        "active": True,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Chains",
        "email": "alicechains@example.com",
        "hashed_password": hash_password("12345"),
        "active": True,
    },
}

refresh_tokens = defaultdict(set)


class Token(BaseModel):
    refresh_token: str
    access_token: str
    token_type: str


class UserSchema(BaseModel):
    username: str
    full_name: str
    email: str
    active: bool


class UserInDB(UserSchema):
    hashed_password: bytes


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


def create_token(data: dict, expires_delta: datetime.timedelta, token_type: str):
    encoded_jwt = jwt.encode(
        payload={
            **data,
            "exp": datetime.datetime.now(datetime.timezone.utc) + expires_delta,
            "token_type": token_type,
        },
        key=SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def validate_token(token: str, token_type: str):
    payload: dict = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("token_type") != token_type:
        raise PyJWTError()
    return payload


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


def get_user_from_db_by_username(
    username: str,
) -> UserInDB | None:
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)


def get_user_schema_by_username(
    username: str,
) -> UserSchema:
    user_dict = fake_users_db[username]
    return UserSchema(**user_dict)


def authenticate_user(username: str, password: str) -> UserInDB:
    user = get_user_from_db_by_username(username)
    if user and validate_password(
        password=password,
        hashed_password=user.hashed_password,
    ):
        return user

    return None


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UserSchema:
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
        payload: dict = validate_token(token=token, token_type="access")
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)

    except (PyJWTError, ValidationError):
        raise credentials_exception

    user = get_user_schema_by_username(username=token_data.username)

    if user is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


async def get_current_active_user(
    current_user: Annotated[UserSchema, Security(get_current_user)],
) -> UserSchema:
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


def is_refresh_token_valid(username: str, token: str) -> bool:
    return token in refresh_tokens[username]


def create_tokens(data: dict) -> Token:
    refresh_token = create_token(
        data=data,
        expires_delta=datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
        token_type="refresh",
    )
    access_token = create_token(
        data=data,
        expires_delta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )
    refresh_tokens[data["sub"]].add(refresh_token)
    return Token(
        refresh_token=refresh_token, access_token=access_token, token_type="bearer"
    )


@app.post("/token/")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = authenticate_user(
        username=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return create_tokens(
        {
            "sub": user.username,  # it is better to use the user's ID
            "scopes": form_data.scopes,
        }
    )


@app.get("/refresh-token/")
def refresh(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = validate_token(token=token, token_type="refresh")
        if not is_refresh_token_valid(username=payload["sub"], token=token):
            raise PyJWTError()
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )
    tokens = create_tokens(
        {
            "sub": payload["sub"],
            "scopes": payload["scopes"],
        }
    )
    refresh_tokens[payload["sub"]].discard(token)
    return tokens


@app.get("/introspect/")
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


@app.get("/me/")
def get_me(user: UserSchema = Security(get_access_token, scopes=["me"])):
    return user
