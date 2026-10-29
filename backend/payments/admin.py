from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "course",
        "provider",
        "status",
        "amount",
        "currency",
        "paid_at",
        "created_at",
    )
    list_filter = ("provider", "status", "currency", "created_at")
    search_fields = (
        "user__email",
        "course__title",
        "provider_payment_id",
        "external_reference",
    )
    readonly_fields = ("created_at", "updated_at", "paid_at")
