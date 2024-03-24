import datetime
from datetime import timedelta
from uuid import uuid4

from src.config import settings
from src.emails.schemas import EmailTokenPayload
from src.emails.token_utils import gen_email_token
from src.emails.utils import send_email
from src.redis_helper import redis_client

RECOVERY_PASSWORD_TOKEN_EXPIRE_SECONDS = 1 * 60 * 60  # 1 hour
VERIFY_EMAIL_TOKEN_EXPIRE_SECONDS = 1 * 60 * 60  # 1 hour


async def send_reset_password_email(email_to: str) -> None:
    jti = uuid4()
    payload = EmailTokenPayload(
        sub=email_to,
        typ="email",
        jti=jti,
        exp=datetime.datetime.now(datetime.UTC)
        + timedelta(seconds=RECOVERY_PASSWORD_TOKEN_EXPIRE_SECONDS),
    )
    token = gen_email_token(payload=payload)
    await redis_client.set(
        f"reset_password_token_id_{email_to}",
        jti,
        ex=RECOVERY_PASSWORD_TOKEN_EXPIRE_SECONDS,
    )
    send_email(
        email_to=email_to,
        subject=f"{settings.PROJECT_NAME} - Password recovery for user {email_to}",
        html_body=f"<p>Use the token to recovery your password: {token}</p>",
    )


async def send_verify_email(email_to: str, username: str) -> None:
    jti = uuid4()
    payload = EmailTokenPayload(
        sub=email_to,
        typ="email",
        jti=jti,
        exp=datetime.datetime.now(datetime.UTC)
        + timedelta(seconds=VERIFY_EMAIL_TOKEN_EXPIRE_SECONDS),
    )
    token = gen_email_token(payload=payload)
    await redis_client.set(
        f"verify_email_token_id_{email_to}",
        jti,
        ex=VERIFY_EMAIL_TOKEN_EXPIRE_SECONDS
    )
    send_email(
        email_to=email_to,
        subject=f"{settings.PROJECT_NAME} - Verify email for user {username}",
        html_body=(
            f"<p>Use the following token to verify your email address.</p>\n"
            f"Token: {token}"
        ),
    )


# def send_otp_email(email_to: str, username: str, opt: str) -> None:
#     send_email(
#         email_to=email_to,
#         subject="OTP",
#         html_body=f"Hello, {username}\nCode: {opt}",
#     )
