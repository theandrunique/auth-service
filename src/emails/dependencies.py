from typing import Annotated
from uuid import UUID

from fastapi import Security
from redis.asyncio import Redis

from src.redis import RedisClient

from .exceptions import InvalidToken
from .schemas import EmailToken
from .utils import validate_email_token


async def check_token(token: str, key_prefix: str, redis: Redis) -> UUID:
    payload = validate_email_token(token)
    if payload is None:
        raise InvalidToken()

    expected_jti = await redis.get(f"{key_prefix}{payload.sub}")
    if UUID(hex=expected_jti) != payload.jti:
        raise InvalidToken()
    await redis.delete(f"{key_prefix}{payload.sub}")

    return payload.sub


async def check_reset_password_token(data: EmailToken, redis: RedisClient) -> UUID:
    return await check_token(
        token=data.token, key_prefix="reset_password_token_id_", redis=redis
    )


ResetPassEmailDep = Annotated[str, Security(check_reset_password_token)]


async def check_verify_email_token(data: EmailToken, redis: RedisClient) -> UUID:
    return await check_token(
        token=data.token, key_prefix="verify_email_token_id_", redis=redis
    )


VerifyEmailDep = Annotated[str, Security(check_verify_email_token)]
