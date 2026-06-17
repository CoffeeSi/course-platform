from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_verification_email(user_email, code):
    subject = "Подтверждение регистрации на платформе"
    message = f"Добро пожаловать! Ваш код для подтверждения Email: {code}"
    print(f"Отправка письма на {user_email} с кодом {code}")

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        connection=None,
    )

    return f"Письмо успешно отправлено на {user_email}"
