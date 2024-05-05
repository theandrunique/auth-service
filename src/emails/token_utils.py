from pydantic import ValidationError

from src import jwt_token

from .schemas import EmailTokenPayload


def gen_email_token(
    payload: EmailTokenPayload,
) -> str:
    return jwt_token.create(payload=payload.model_dump())


def validate_email_token(token: str) -> EmailTokenPayload | None:
    payload = jwt_token.decode(token)
    if not payload:
        return None
    try:
        return EmailTokenPayload(**payload)
    except ValidationError:
        return None
