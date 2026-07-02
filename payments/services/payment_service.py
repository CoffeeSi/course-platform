from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.utils import timezone

from courses.models import Course
from enrollments.models import Enrollment
from .registry import get_payment_provider
from payments.models import Payment


class PaymentService:
    def create_payment(
        self, *, user, course: Course, provider_code: str
    ) -> tuple[Payment, dict]:
        provider = get_payment_provider(provider_code)
        payment = Payment.objects.create(
            user=user,
            course=course,
            provider=provider_code,
            amount=course.price,
            currency=getattr(settings, "PAYMENT_DEFAULT_CURRENCY", "USD"),
            status=Payment.Status.PENDING,
        )
        checkout_payload = provider.build_checkout_payload(payment)
        if not checkout_payload.get("checkout_url"):
            payment.status = Payment.Status.FAILED
            payment.error_message = "Provider did not return a checkout URL."
            payment.save(update_fields=["status", "error_message", "updated_at"])
            raise ImproperlyConfigured("Payment provider is currently unavailable.")
        payment.metadata = {
            **payment.metadata,
            "checkout_payload": checkout_payload,
        }
        payment.provider_payment_id = (
            checkout_payload.get("provider_payment_id") or None
        )
        payment.checkout_url = checkout_payload.get("checkout_url", "")
        payment.external_reference = checkout_payload.get("external_reference", "")
        payment.save(
            update_fields=[
                "metadata",
                "provider_payment_id",
                "checkout_url",
                "external_reference",
                "updated_at",
            ]
        )
        return payment, checkout_payload

    @transaction.atomic
    def mark_payment_succeeded(self, payment: Payment, provider_event: dict) -> Payment:
        payment.status = Payment.Status.SUCCEEDED
        payment.provider_payment_id = (
            provider_event.get("provider_payment_id") or payment.provider_payment_id
        )
        payment.paid_at = timezone.now()
        payment.metadata = {
            **payment.metadata,
            "provider_event": provider_event,
        }
        payment.error_message = ""
        payment.save(
            update_fields=[
                "status",
                "provider_payment_id",
                "paid_at",
                "metadata",
                "error_message",
                "updated_at",
            ]
        )

        Enrollment.objects.get_or_create(student=payment.user, course=payment.course)
        return payment

    @transaction.atomic
    def mark_payment_failed(self, payment: Payment, provider_event: dict) -> Payment:
        payment.status = Payment.Status.FAILED
        payment.error_message = provider_event.get("error_message", "")
        payment.metadata = {
            **payment.metadata,
            "provider_event": provider_event,
        }
        payment.save(
            update_fields=["status", "error_message", "metadata", "updated_at"]
        )
        return payment

    def handle_webhook(self, provider_code: str, payload: dict) -> Payment:
        provider = get_payment_provider(provider_code)
        event = provider.parse_webhook(payload)
        internal_payment_id = event.get("payment_id")
        provider_payment_id = event.get("provider_payment_id")

        payment = None
        if internal_payment_id:
            payment = Payment.objects.filter(
                id=internal_payment_id,
                provider=provider_code,
            ).first()

        if not payment and provider_payment_id:
            payment = Payment.objects.filter(
                provider=provider_code,
                provider_payment_id=provider_payment_id,
            ).first()

        if not payment:
            external_reference = event.get("external_reference", "")
            if external_reference:
                payment = Payment.objects.filter(
                    provider=provider_code,
                    external_reference=external_reference,
                ).first()

        if not payment:
            raise ImproperlyConfigured(
                "Webhook payload must include a known payment identifier."
            )

        status = event.get("status")

        if status in {
            Payment.Status.SUCCEEDED,
            "paid",
            "success",
            "succeeded",
            "completed",
        }:
            return self.mark_payment_succeeded(payment, event)

        if status in {
            Payment.Status.FAILED,
            "failed",
            "canceled",
            "cancelled",
            "declined",
        }:
            return self.mark_payment_failed(payment, event)

        return payment
