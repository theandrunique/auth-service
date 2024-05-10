from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from .config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_SERVER,
    MAIL_FROM_NAME=settings.FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fm = FastMail(conf)


async def send_email(
    email_to: str,
    subject: str,
    html_body: str,
) -> None:
    message = MessageSchema(
        subject=subject, recipients=[email_to], body=html_body, subtype=MessageType.html
    )
    await fm.send_message(message)
