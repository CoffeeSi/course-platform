from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiExample
from users.views import (
    RegisterView,
    VerifyEmailView,
    ResendVerificationEmailView,
    CurrentUserProfileView,
)


# Расширенные JWT views с документацией
@extend_schema(
    summary="Вход и получение токена доступа",
    description="Аутентификация пользователя с email и пароля для получения JWT токена доступа.",
    request={
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "format": "email",
                "example": "user@example.com",
            },
            "password": {"type": "string", "example": "password123"},
        },
    },
    responses={
        200: OpenApiExample(
            "Успешно",
            value={
                "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            },
        ),
        401: OpenApiExample(
            "Неавторизованный доступ",
            value={
                "detail": "Не найден активный аккаунт с указанными учетными данными"
            },
        ),
    },
    tags=["Аутентификация"],
)
class DocumentedTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(
    summary="Обновление токена доступа",
    description="Получить новый токен доступа используя валидный токен обновления.",
    request={
        "type": "object",
        "properties": {
            "refresh": {
                "type": "string",
                "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            }
        },
    },
    responses={
        200: OpenApiExample(
            "Успешно", value={"access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        ),
        401: OpenApiExample(
            "Неверный токен", value={"detail": "Токен неверный или истек"}
        ),
    },
    tags=["Аутентификация"],
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
