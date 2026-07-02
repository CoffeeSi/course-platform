from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
import stripe

from payments.models import Payment


@dataclass
class CheckoutSession:
    checkout_url: str | None = None
    provider_payment_id: str | None = None
    payload: dict[str, Any] | None = None


class BasePaymentProvider(ABC):
    code: str

    @abstractmethod
    def build_checkout_payload(self, payment: Payment) -> dict[str, Any]:
        raise NotImplementedError

    def parse_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        return payload


class StripePaymentProvider(BasePaymentProvider):
    code = Payment.Provider.STRIPE

    def build_checkout_payload(self, payment: Payment) -> dict[str, Any]:
        stripe_secret_key = getattr(settings, "STRIPE_SECRET_KEY", "")
        success_url = getattr(settings, "STRIPE_SUCCESS_URL", "")
        cancel_url = getattr(settings, "STRIPE_CANCEL_URL", "")

        if not stripe_secret_key:
            raise ImproperlyConfigured("STRIPE_SECRET_KEY is not configured.")
        if not success_url or not cancel_url:
            raise ImproperlyConfigured(
                "STRIPE_SUCCESS_URL and STRIPE_CANCEL_URL must be configured."
            )

        stripe.api_key = stripe_secret_key

        metadata = {
            "payment_id": str(payment.id),
            "course_id": str(payment.course.id),
            "user_id": str(payment.user.id),
        }

        unit_amount = int(
            (Decimal(payment.amount) * Decimal("100")).quantize(Decimal("1"))
        )
        session = stripe.checkout.Session.create(
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=str(payment.id),
            metadata=metadata,
            line_items=[
                {
                    "price_data": {
                        "currency": payment.currency.lower(),
                        "unit_amount": unit_amount,
                        "product_data": {
                            "name": payment.course.title,
                        },
                    },
                    "quantity": 1,
                }
            ],
            payment_intent_data={"metadata": metadata},
        )

        return {
            "provider": self.code,
            "amount": str(payment.amount),
            "currency": payment.currency,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "webhook_secret": getattr(settings, "STRIPE_WEBHOOK_SECRET", ""),
            "mode": "payment",
            "metadata": metadata,
            "checkout_url": session.url,
            "provider_payment_id": session.id,
            "external_reference": (
                str(session.payment_intent) if session.payment_intent else ""
            ),
        }

    def parse_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
        stripe_signature = payload.get("_stripe_signature", "")
        raw_body = payload.get("_raw_body")

        if webhook_secret and raw_body and stripe_signature:
            event = stripe.Webhook.construct_event(
                payload=raw_body,
                sig_header=stripe_signature,
                secret=webhook_secret,
            )
            if hasattr(event, "to_dict"):
                event = event.to_dict()
        else:
            event = payload.get("_json_body", payload)

        event_type = payload.get("event_type") or ""
        event_data: dict[str, Any] = {}

        if isinstance(event, dict):
            event_type = event.get("type") or event_type
            event_data = (event.get("data") or {}).get("object") or {}
        else:
            event_type = getattr(event, "type", "") or event_type
            data_wrapper = getattr(event, "data", None)
            stripe_object = getattr(data_wrapper, "object", None)

            if hasattr(stripe_object, "to_dict"):
                event_data = stripe_object.to_dict()
            else:
                event_data = dict(stripe_object)

        metadata = event_data.get("metadata", {}) or {}

        payment_id = metadata.get("payment_id") or event_data.get("client_reference_id")
        provider_payment_id = event_data.get("id") or payload.get(
            "provider_payment_id", ""
        )

        external_reference = event_data.get("payment_intent") or payload.get(
            "external_reference", ""
        )

        normalized_status = None
        error_message = ""

        if event_type in {
            "checkout.session.completed",
            "checkout.session.async_payment_succeeded",
            "payment_intent.succeeded",
        }:
            normalized_status = Payment.Status.SUCCEEDED

        elif event_type in {
            "checkout.session.expired",
            "checkout.session.async_payment_failed",
            "payment_intent.payment_failed",
        }:
            normalized_status = Payment.Status.FAILED
            error_message = "Stripe reports payment failure."

        if not payment_id and not provider_payment_id and not external_reference:
            raise ImproperlyConfigured(
                "Stripe webhook does not contain any payment identifiers."
            )

        return {
            "event_type": event_type,
            "payment_id": payment_id,
            "provider_payment_id": (
                str(provider_payment_id) if provider_payment_id else ""
            ),
            "external_reference": external_reference,
            "status": normalized_status,
            "error_message": error_message,
            "raw_event": event,
        }


class FreedomPayProvider(BasePaymentProvider):
    code = Payment.Provider.FREEDOMPAY

    def build_checkout_payload(self, payment: Payment) -> dict[str, Any]:
        return {
            "provider": self.code,
            "amount": str(payment.amount),
            "currency": payment.currency,
            "merchant_id": getattr(settings, "FREEDOMPAY_MERCHANT_ID", ""),
            "return_url": getattr(settings, "FREEDOMPAY_RETURN_URL", ""),
            "callback_url": getattr(settings, "FREEDOMPAY_CALLBACK_URL", ""),
            "signature_key": getattr(settings, "FREEDOMPAY_SIGNATURE_KEY", ""),
            "order": {
                "payment_id": payment.id,
                "course_id": payment.course.id,
                "user_id": payment.user.id,
                "title": payment.course.title,
            },
        }
