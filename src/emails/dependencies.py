from typing import Annotated

from fastapi import Security

from src.redis_helper import redis_client

from .exceptions import InvalidToken
from .schemas import EmailToken
from .token_utils import check_email_token


async def check_token(data: EmailToken, key: str) -> str:
    payload = check_email_token(token=data.token)
    if payload is None:
        raise InvalidToken()

    expected_jti = await redis_client.get(f"{key}{payload.sub}")
    if expected_jti != payload.jti:
        raise InvalidToken()
    await redis_client.delete(f"{key}{payload.sub}")

    return payload.sub

async def check_reset_password_token(token: str) -> str:
    return await check_token(token=token, key="reset_password_token_id_")


ResetPassEmailDep = Annotated[str, Security(check_reset_password_token)]


async def check_verify_email_token(token: str) -> str:
    return await check_token(token=token, key="verify_email_token_id_")


VerifyEmailDep = Annotated[str, Security(check_verify_email_token)]
