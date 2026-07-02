from django.urls import path

from .views import (
    PaymentCreateView,
    PaymentListView,
    PaymentWebhookView,
    VerifySessionView,
)

urlpatterns = [
    path("", PaymentListView.as_view(), name="payment-list"),
    path("create/", PaymentCreateView.as_view(), name="payment-create"),
    path(
        "webhooks/<str:provider_code>/",
        PaymentWebhookView.as_view(),
        name="payment-webhook",
    ),
    path("verify-session/", VerifySessionView.as_view(), name="verify-session"),
]
