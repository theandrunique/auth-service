from dataclasses import asdict

from pydantic import ValidationError

from src import jwt_token
from src.config import settings as global_settings
from src.emails.schemas import (
    EmailTokenPayloadValidator,
    ResetPasswordTokenPayload,
    VerificationTokenPayload,
)

from .config import settings
from .smtp import send_email
from .templates import render_email_template


def gen_email_token(
    payload: ResetPasswordTokenPayload | VerificationTokenPayload,
) -> str:
    return jwt_token.create(payload=asdict(payload))


def validate_email_token(token: str) -> EmailTokenPayloadValidator | None:
    payload = jwt_token.decode(token)
    if not payload:
        return None
    try:
        return EmailTokenPayloadValidator(**payload)
    except ValidationError:
        return None


async def send_reset_password_email(
    email_to: str, payload: ResetPasswordTokenPayload
) -> None:
    token = gen_email_token(payload=payload)
    subject = f"{global_settings.PROJECT_NAME} - Password recovery for user {email_to}"
    send_email(
        email_to=email_to,
        subject=subject,
        html_body=await render_email_template(
            template_name="reset_password.html",
            context={"token": token},
        ),
    )


async def send_verify_email(
    email_to: str, username: str, payload: VerificationTokenPayload
) -> None:
    token = gen_email_token(payload=payload)
    confirm_url = (
        f"{global_settings.FRONTEND_URL}{settings.CONFIRM_FRONTEND_URI}?token={token}"
    )
    send_email(
        email_to=email_to,
        subject=f"{global_settings.PROJECT_NAME} - Verify email for user {username}",
        html_body=await render_email_template(
            template_name="confirm_email.html",
            context={
                "username": username,
                "confirm_url": confirm_url,
            },
        ),
    )
