from abc import ABC, abstractmethod

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from src.config import settings


class IEmailService(ABC):
    @abstractmethod
    async def send(self, email_to: str, subject: str, html_body: str) -> None: ...


class EmailService(IEmailService):
    def __init__(self) -> None:
        conf = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USER,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM=settings.FROM_EMAIL,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_SERVER,
            MAIL_FROM_NAME=settings.FROM_NAME,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )

        self.fm = FastMail(conf)

    async def send_email(
        self,
        email_to: str,
        subject: str,
        html_body: str,
    ) -> None:
        message = MessageSchema(subject=subject, recipients=[email_to], body=html_body, subtype=MessageType.html)
        await self.fm.send_message(message)
