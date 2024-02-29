import datetime
import uuid
import bcrypt
import jwt
from jwt.exceptions import PyJWTError
import secrets
from config import settings
from .schemas import TokenPair, TokenType, TokenPayload


def gen_key():
    return secrets.token_hex(settings.REFRESH_TOKEN_LENGTH_BYTES)


def gen_random_token_id():
    return str(uuid.uuid4())


def _create_token(data: dict, expires_delta: datetime.timedelta, token_type: TokenType):
    encoded_jwt = jwt.encode(
        payload={
            **data,
            "exp": datetime.datetime.now(datetime.timezone.utc) + expires_delta,
            "token_type": token_type.value,
        },
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def validate_token(token: str, token_type: TokenType) -> TokenPayload:
    payload_dict: dict = jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    payload = TokenPayload(**payload_dict)
    if payload_dict["token_type"] != token_type.value:
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


def create_tokens(payload: TokenPayload) -> TokenPair:
    payload_dict = payload.model_dump()
    access_token = _create_token(
        data=payload_dict,
        expires_delta=datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type=TokenType.ACCESS,
    )
    refresh_token = _create_token(
        data=payload_dict,
        expires_delta=datetime.timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
        token_type=TokenType.REFRESH,
    )
    return TokenPair(
        refresh_token=refresh_token, access_token=access_token, token_type="Bearer"
    )
