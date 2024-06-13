from typing import Annotated
from uuid import UUID

from fastapi import Security

from .exceptions import InvalidToken
from .schemas import EmailAudience, EmailToken
from .utils import validate_email_token


def check_token(token: str, audience: EmailAudience) -> UUID:
    payload = validate_email_token(token)
    if payload is None:
        raise InvalidToken()
    if payload.aud != audience:
        raise InvalidToken()

    return payload.sub


def check_reset_password_token(data: EmailToken) -> UUID:
    return check_token(token=data.token, audience=EmailAudience.RESET_PASSWORD)


ResetPassEmailDep = Annotated[UUID, Security(check_reset_password_token)]


def check_verify_email_token(data: EmailToken) -> UUID:
    return check_token(
        token=data.token,
        audience=EmailAudience.EMAIL_CONFIRMATION,
    )


VerifyEmailDep = Annotated[UUID, Security(check_verify_email_token)]
