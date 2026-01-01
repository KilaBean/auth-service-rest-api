from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.config import settings

# Configuration pulls directly from settings (which reads .env)
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=True
)

fm = FastMail(conf)

async def send_reset_email(email_to: EmailStr, token: str):
    """
    Sends a password reset email with the token embedded in a link.
    """
    
    # In a real React app, this would be: https://myapp.com/reset-password?token=...
    # For now, pointing to docs
    reset_link = f"http://localhost:8000/docs?token={token}"

    html = f"""
    <p>Hello,</p>
    <p>You requested to reset your password. Click the link below to reset it:</p>
    <p>
        <a href="{reset_link}">Reset Password</a>
    </p>
    <p>This link is valid for 30 minutes.</p>
    <p>If you did not request this, please ignore this email.</p>
    """

    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email_to],
        body=html,
        subtype="html"
    )

    await fm.send_message(message)