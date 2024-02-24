import datetime
import bcrypt
import jwt
from jwt.exceptions import PyJWTError
import secrets
from config import (
    REFRESH_TOKEN_LENGTH_BYTES,
    SECRET_KEY,
    ALGORITHM,
)



def gen_key():
    return secrets.token_hex(REFRESH_TOKEN_LENGTH_BYTES)


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


def create_refresh_token(data: dict, expires_delta: datetime.timedelta):
    encoded_jwt = jwt.encode(
        payload={
            **data,
            "exp": datetime.datetime.now(datetime.timezone.utc) + expires_delta,
            "token_type": "refresh",
        },
        key=SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def create_access_token(data: dict, expires_delta: datetime.timedelta):
    encoded_jwt = jwt.encode(
        payload={
            **data,
            "exp": datetime.datetime.now(datetime.timezone.utc) + expires_delta,
            "token_type": "access",
        },
        key=SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def validate_token(token: str, token_type: str):
    payload: dict = jwt.decode(
        jwt=token,
        key=SECRET_KEY,
        algorithms=[ALGORITHM],
    )
    if payload.get("token_type") != token_type:
        raise PyJWTError()
    return payload


def validate_access_token(token: str):
    payload: dict = jwt.decode(
        jwt=token,
        key=SECRET_KEY,
        algorithms=[ALGORITHM],
    )
    if payload.get("token_type") != "access":
        raise PyJWTError()
    return payload


def validate_refresh_token(token: str):
    payload: dict = jwt.decode(
        jwt=token,
        key=SECRET_KEY,
        algorithms=[ALGORITHM],
    )
    if payload.get("token_type") != "refresh":
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
    
    
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(
        password=password.encode(),
        salt=bcrypt.gensalt(),
    )