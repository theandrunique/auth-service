import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import settings


def send_email(
    email_to: str,
    subject: str,
    html_body: str,
) -> None:
    msg = MIMEMultipart()
    msg["From"] = f"{settings.EMAILS_FROM_NAME} {settings.EMAILS_FROM_EMAIL}"
    msg["To"] = email_to
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    server = smtplib.SMTP_SSL(settings.SMTP.SERVER, settings.SMTP.PORT)
    server.login(settings.SMTP.USER, settings.SMTP.PASSWORD)
    server.send_message(msg=msg)
    server.quit()
