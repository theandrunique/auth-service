import datetime
import secrets
import smtplib
import string
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any
from uuid import UUID

import jinja2

from src.config import settings as global_settings
from src.emails.schemas import EmailTokenPayload
from src.emails.token_utils import gen_email_token

from .config import settings

template_loader = jinja2.FileSystemLoader(settings.TEMPLATES_DIR)
template_env = jinja2.Environment(enable_async=True, loader=template_loader)


async def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template = template_env.get_template(template_name)
    return await template.render_async(context)


def send_email(
    email_to: str,
    subject: str,
    html_body: str,
) -> None:
    msg = MIMEMultipart()
    msg["From"] = f"{settings.FROM_NAME} {settings.FROM_EMAIL}"
    msg["To"] = email_to
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    server = smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT)
    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    server.send_message(msg=msg)
    server.quit()


async def send_reset_password_email(email_to: str, jti: UUID) -> None:
    payload = EmailTokenPayload(
        sub=email_to,
        typ="email",
        jti=jti,
        exp=datetime.datetime.now(datetime.UTC)
        + timedelta(seconds=settings.RESET_TOKEN_EXPIRE_SECONDS),
    )
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


async def send_verify_email(email_to: str, username: str, jti: UUID) -> None:
    payload = EmailTokenPayload(
        sub=email_to,
        typ="email",
        jti=jti,
        exp=datetime.datetime.now(datetime.UTC)
        + timedelta(seconds=settings.VERIFICATION_TOKEN_EXPIRE_SECONDS),
    )
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


async def send_otp_email(email_to: str, username: str, otp: str, token: str) -> None:
    send_email(
        email_to=email_to,
        subject="OTP",
        html_body=await render_email_template(
            template_name="otp.html",
            context={"username": username, "otp": otp},
        ),
    )


def gen_otp_with_token() -> tuple[str, str]:
    otp = "".join(secrets.choice(string.digits) for _ in range(6))
    token = secrets.token_urlsafe(40)
    return otp, token
