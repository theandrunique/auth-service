import datetime
import smtplib
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any
from uuid import uuid4

import jinja2

from src.config import settings as global_settings
from src.emails.schemas import EmailTokenPayload
from src.emails.token_utils import gen_email_token
from src.redis_helper import redis_client

from .config import settings

template_loader = jinja2.FileSystemLoader(settings.EMAILS_TEMPLATES_DIR)
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
    msg["From"] = f"{settings.SMTP_FROM_NAME} {settings.SMTP_FROM_EMAIL}"
    msg["To"] = email_to
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    server = smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT)
    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    server.send_message(msg=msg)
    server.quit()


async def send_reset_password_email(email_to: str) -> None:
    jti = uuid4()
    payload = EmailTokenPayload(
        sub=email_to,
        typ="email",
        jti=jti,
        exp=datetime.datetime.now(datetime.UTC)
        + timedelta(seconds=settings.RESET_PASSWORD_TOKEN_EXPIRE_SECONDS),
    )
    token = gen_email_token(payload=payload)
    await redis_client.set(
        f"reset_password_token_id_{email_to}",
        jti.bytes,
        ex=settings.RESET_PASSWORD_TOKEN_EXPIRE_SECONDS,
    )
    subject = f"{global_settings.PROJECT_NAME} - Password recovery for user {email_to}"
    send_email(
        email_to=email_to,
        subject=subject,
        html_body=await render_email_template(
            template_name="reset_password.html",
            context={"token": token},
        ),
    )


async def send_verify_email(email_to: str, username: str) -> None:
    jti = uuid4()
    payload = EmailTokenPayload(
        sub=email_to,
        typ="email",
        jti=jti,
        exp=datetime.datetime.now(datetime.UTC)
        + timedelta(seconds=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_SECONDS),
    )
    token = gen_email_token(payload=payload)
    await redis_client.set(
        f"verify_email_token_id_{email_to}",
        jti.bytes,
        ex=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_SECONDS,
    )
    confirm_url = f"{global_settings.FRONTEND_URL}{settings.EMAIL_CONFIRM_FRONTEND_URI}?token={token}"
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
    await redis_client.set(
        f"otp_{email_to}_{token}", otp, ex=settings.OTP_EXPIRES_SECONDS
    )
    send_email(
        email_to=email_to,
        subject="OTP",
        html_body=await render_email_template(
            template_name="otp.html",
            context={"username": username, "otp": otp},
        ),
    )
