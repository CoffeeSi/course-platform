from django.urls import path
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, inline_serializer

from users.views import (
    RegisterView,
    VerifyEmailView,
    ResendVerificationEmailView,
    CurrentUserProfileView,
)


@extend_schema(
    summary="Login and obtain access token",
    description="Authenticate by email and password to receive JWT tokens.",
    request=TokenObtainPairSerializer,
    responses={
        200: inline_serializer(
            name="TokenObtainPairResponse",
            fields={
                "access": serializers.CharField(),
                "refresh": serializers.CharField(),
            },
        ),
        401: inline_serializer(
            name="TokenAuthErrorResponse",
            fields={"detail": serializers.CharField()},
        ),
    },
    tags=["Authentication"],
)
class DocumentedTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(
    summary="Refresh access token",
    description="Use a valid refresh token to receive a new access token.",
    request=TokenRefreshSerializer,
    responses={
        200: inline_serializer(
            name="TokenRefreshResponse",
            fields={"access": serializers.CharField()},
        ),
        401: inline_serializer(
            name="TokenRefreshErrorResponse",
            fields={"detail": serializers.CharField()},
        ),
    },
    tags=["Authentication"],
)
class DocumentedTokenRefreshView(TokenRefreshView):
    pass


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path(
        "resend-email-verification/",
        ResendVerificationEmailView.as_view(),
        name="resend-email-verification",
    ),
    path("profile/", CurrentUserProfileView.as_view(), name="profile"),
    path("login/", DocumentedTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", DocumentedTokenRefreshView.as_view(), name="token_refresh"),
]
