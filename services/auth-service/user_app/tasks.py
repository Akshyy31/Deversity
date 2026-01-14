
from celery import shared_task
from user_app.email import send_verification_email

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    retry_backoff=True,
)
def send_verification_email_task(self, email: str, token: str):
    send_verification_email(email=email, token=token)
