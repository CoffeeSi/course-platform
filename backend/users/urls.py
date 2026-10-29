from django.urls import path
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from drf_spectacular.utils import extend_schema, inline_serializer
from users.views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    RegisterView,
    VerifyEmailView,
    ResendVerificationEmailView,
    CurrentUserProfileView,
)


@extend_schema(
    summary="Аутентификация пользователя и получение access токена",
    description="Аутентификация пользователя и получение access токена. Токен возвращается в HttpOnly cookie.",
    request=TokenObtainPairSerializer,
    responses={
        200: inline_serializer(
            name="LoginResponse",
            fields={"message": serializers.CharField()},
        ),
        401: inline_serializer(
            name="TokenAuthErrorResponse",
            fields={"detail": serializers.CharField()},
        ),
    },
    tags=["Аутентификация"],
)
class DocumentedTokenObtainPairView(CookieTokenObtainPairView):
    pass


@extend_schema(
    summary="Обновление access токена с использованием refresh токена",
    description="Обновление access токена с использованием refresh токена в HttpOnly cookie.",
    request=TokenRefreshSerializer,
    responses={
        200: inline_serializer(
            name="TokenRefreshResponse",
            fields={"message": serializers.CharField()},
        ),
        401: inline_serializer(
            name="TokenRefreshErrorResponse",
            fields={"detail": serializers.CharField()},
        ),
    },
    tags=["Аутентификация"],
)
class DocumentedTokenRefreshView(CookieTokenRefreshView):
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
    path("logout/", LogoutView.as_view(), name="logout"),
]
