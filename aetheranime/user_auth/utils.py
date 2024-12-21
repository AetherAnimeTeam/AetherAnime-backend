import random
from django.core.mail import send_mail


def generate_verification_code():
    return str(random.randint(100000, 999999))


def send_verification_email(email, code):
    subject = "Verify your email"
    message = f"Your verification code is: {code}"
    from_email = "aetheranime@gmail.com"
    send_mail(subject, message, from_email, [email])
