from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_otp_email(self, email, otp):
    """
    Sends OTP email asynchronously.
    Retries automatically on failure.
    """

    subject = "Your OTP for Account Verification"
    message = f"""
Your One-Time Password (OTP) is:

{otp}

This OTP is valid for 5 minutes.
Do not share this with anyone.
"""

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as exc:
        # 🔁 Retry on transient failures (SMTP, network, etc.)
        raise self.retry(exc=exc)
