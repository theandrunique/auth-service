from dataclasses import asdict

from pydantic import ValidationError

from src import jwt_token
from src.config import settings as global_settings
from src.emails.schemas import (
    EmailTokenPayloadValidator,
    ResetPasswordTokenPayload,
    VerificationTokenPayload,
)
from src.users.schemas import UserSchema

from .config import settings
from .smtp import send_email
from .templates import render_email_template


def gen_email_token(
    payload: ResetPasswordTokenPayload | VerificationTokenPayload,
) -> str:
    return jwt_token.create(payload=asdict(payload))


def validate_email_token(
    token: str, audience: str
) -> EmailTokenPayloadValidator | None:
    payload = jwt_token.decode(token, audience=audience)
    if not payload:
        return None
    try:
        return EmailTokenPayloadValidator(**payload)
    except ValidationError:
        return None


async def send_reset_password_email(user: UserSchema) -> None:
    token = gen_email_token(payload=ResetPasswordTokenPayload(sub=user.id))
    subject = (
        f"{global_settings.PROJECT_NAME} - Password recovery for user {user.username}"
    )
    await send_email(
        email_to=user.email,
        subject=subject,
        html_body=await render_email_template(
            template_name="reset_password.html",
            context={"token": token},
        ),
    )


async def send_verify_email(user: UserSchema) -> None:
    token = gen_email_token(payload=VerificationTokenPayload(sub=user.id))
    confirm_url = (
        f"{global_settings.FRONTEND_URL}{settings.CONFIRM_FRONTEND_URI}?token={token}"
    )
    subject = f"{global_settings.PROJECT_NAME} - Verify email for user {user.username}"
    await send_email(
        email_to=user.email,
        subject=subject,
        html_body=await render_email_template(
            template_name="confirm_email.html",
            context={
                "username": user.username,
                "confirm_url": confirm_url,
            },
        ),
    )
