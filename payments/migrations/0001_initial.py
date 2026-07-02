# Generated manually for payments app scaffold.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("courses", "0004_alter_course_id_alter_lesson_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                        verbose_name="ID",
                    ),
                ),
                (
                    "provider",
                    models.CharField(
                        choices=[("stripe", "Stripe"), ("freedompay", "FreedomPay")],
                        max_length=20,
                        verbose_name="Платежный провайдер",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("processing", "Processing"),
                            ("succeeded", "Succeeded"),
                            ("failed", "Failed"),
                            ("canceled", "Canceled"),
                            ("refunded", "Refunded"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="Сумма"
                    ),
                ),
                (
                    "currency",
                    models.CharField(
                        default="USD", max_length=3, verbose_name="Валюта"
                    ),
                ),
                (
                    "provider_payment_id",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        unique=True,
                        verbose_name="ID платежа в провайдере",
                    ),
                ),
                (
                    "checkout_url",
                    models.URLField(blank=True, verbose_name="Ссылка на оплату"),
                ),
                (
                    "external_reference",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Внешняя ссылка"
                    ),
                ),
                (
                    "metadata",
                    models.JSONField(
                        blank=True, default=dict, verbose_name="Метаданные"
                    ),
                ),
                ("error_message", models.TextField(blank=True, verbose_name="Ошибка")),
                (
                    "paid_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="Оплачен"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Создан"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Обновлен"),
                ),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="courses.course",
                        verbose_name="Курс",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "db_table": "payments",
                "verbose_name": "Платеж",
                "verbose_name_plural": "Платежи",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(fields=["user"], name="payments_us_user_id_1d2f9b_idx"),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(
                fields=["course"], name="payments_co_course_i_83d7a2_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(
                fields=["provider"], name="payments_pr_provider_52cb96_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(fields=["status"], name="payments_st_status_0a8a2c_idx"),
        ),
    ]
