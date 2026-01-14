# users/email.py
from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(email: str, token: str):
    verify_link = f"{settings.FRONTEND_BASE_URL}/auth/verify-email/?token={token}"

    send_mail(
        subject="Verify your email",
        message=(
            "Welcome to DevConnect.\n\n"
            "Click the link below to verify your email:\n\n"
            f"{verify_link}\n\n"
            "This link expires in 15 minutes."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
