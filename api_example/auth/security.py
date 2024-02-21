import datetime
import bcrypt
import jwt
from jwt.exceptions import PyJWTError
import secrets


SECRET_KEY = "381fe4a2683cd0eee27cd66bfe1e5b02142ab7ee64d4f1ccbf1011e7358b005e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
REFRESH_TOKEN_EXPIRE_MINUTES = 24 * 60
REFRESH_TOKEN_LENGTH_BYTES = 24


def gen_key():
    return secrets.token_hex(REFRESH_TOKEN_LENGTH_BYTES)


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