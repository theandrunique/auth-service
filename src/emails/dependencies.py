from typing import Annotated
from uuid import UUID

from fastapi import Security

from src.redis_helper import redis_client

from .exceptions import InvalidOtp, InvalidToken
from .schemas import EmailToken, OtpAuthSchema
from .token_utils import validate_email_token


async def check_token(token: str, key_prefix: str) -> str:
    payload = validate_email_token(token)
    if payload is None:
        raise InvalidToken()

    expected_jti = await redis_client.get(f"{key_prefix}{payload.sub}")
    if UUID(bytes=expected_jti) != payload.jti:
        raise InvalidToken()
    await redis_client.delete(f"{key_prefix}{payload.sub}")

    return payload.sub


async def check_reset_password_token(data: EmailToken) -> str:
    return await check_token(token=data.token, key_prefix="reset_password_token_id_")


ResetPassEmailDep = Annotated[str, Security(check_reset_password_token)]


async def check_verify_email_token(data: EmailToken) -> str:
    return await check_token(token=data.token, key_prefix="verify_email_token_id_")


VerifyEmailDep = Annotated[str, Security(check_verify_email_token)]


async def get_otp(data: OtpAuthSchema) -> str:
    expected_otp = await redis_client.get(f"otp_{data.email}_{data.token}")

    if data.otp != expected_otp:
        raise InvalidOtp()

    await redis_client.delete(f"otp_{data.email}_{data.token}")

    return data.email


OtpEmailDep = Annotated[str, Security(get_otp)]
