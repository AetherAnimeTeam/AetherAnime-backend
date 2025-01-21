import random
from django.core.mail import EmailMessage

from aetheranime import settings


def generate_verification_code():
    return str(random.randint(100000, 999999))


def send_verification_email(email, code):
    email = EmailMessage(
        "Verify your email",
        f"Your verification code is: {code}",
        settings.EMAIL_HOST_USER,
        [email],
    )
    email.send()
