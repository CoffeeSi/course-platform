from django.core.exceptions import ImproperlyConfigured

from payments.models import Payment
from .providers import FreedomPayProvider, StripePaymentProvider, BasePaymentProvider

_PROVIDER_MAP: dict[str, type[BasePaymentProvider]] = {
    Payment.Provider.STRIPE: StripePaymentProvider,
    Payment.Provider.FREEDOMPAY: FreedomPayProvider,
}


def get_payment_provider(provider_code: str) -> BasePaymentProvider:
    provider_class = _PROVIDER_MAP.get(provider_code)
    if not provider_class:
        raise ImproperlyConfigured(f"Unsupported payment provider: {provider_code}")
    return provider_class()
