from django.conf import settings
from django.db import models

from courses.models import Course


class Payment(models.Model):
    class Provider(models.TextChoices):
        STRIPE = "stripe", "Stripe"
        FREEDOMPAY = "freedompay", "FreedomPay"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        CANCELED = "canceled", "Canceled"
        REFUNDED = "refunded", "Refunded"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Курс",
    )
    provider = models.CharField(
        max_length=20,
        choices=Provider.choices,
        verbose_name="Платежный провайдер",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма",
    )
    currency = models.CharField(max_length=3, default="USD", verbose_name="Валюта")
    provider_payment_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        default=None,
        verbose_name="ID платежа в провайдере",
    )
    checkout_url = models.URLField(
        max_length=2048,
        blank=True,
        verbose_name="Ссылка на оплату",
    )
    external_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Внешняя ссылка",
    )
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Метаданные")
    error_message = models.TextField(blank=True, verbose_name="Ошибка")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Оплачен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        db_table = "payments"
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["course"]),
            models.Index(fields=["provider"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.user.email} -> {self.course.title} ({self.provider})"

    @property
    def is_paid(self):
        return self.status == self.Status.SUCCEEDED
