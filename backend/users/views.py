import random

from django.contrib.auth import logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, serializers, status, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.tasks import send_verification_email

from .cookies import REFRESH_COOKIE_NAME, clear_auth_cookies, set_auth_cookies
from .models import Profile, User, Verification
from .serializers import (
    ResendVerificationSerializer,
    UserProfileSerializer,
    UserRegisterSerializer,
    VerificationSerializer,
)


@never_cache
@require_GET
def csrf_token(request):
    return JsonResponse({"csrfToken": get_token(request)})


MessageResponseSerializer = inline_serializer(
    name="MessageResponse",
    fields={"message": serializers.CharField()},
)
ErrorResponseSerializer = inline_serializer(
    name="ErrorResponse",
    fields={"error": serializers.CharField()},
)
ValidationErrorResponseSerializer = inline_serializer(
    name="ValidationErrorResponse",
    fields={"errors": serializers.JSONField()},
)


class RegisterView(views.APIView):
    """
    API endpoint для регистрации пользователя.

    Позволяет неавторизованным пользователям создать новый аккаунт с email и паролем.
    Код подтверждения автоматически отправляется на указанный email.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Регистрация нового пользователя",
        description="Создание нового аккаунта пользователя. 6-значный код подтверждения будет отправлен на указанный email.",
        request=UserRegisterSerializer,
        responses={
            201: MessageResponseSerializer,
            400: ValidationErrorResponseSerializer,
        },
        tags=["Аутентификация"],
    )
    def post(self, request):
        """
        Создание нового аккаунта пользователя.

        Обязательные поля:
        - email: Корректный адрес электронной почты (должен быть уникален)
        - password: Надежный пароль (минимум 8 символов)
        - phone_number (опционально): Номер телефона в любом формате

        Возвращает:
        - 201: Пользователь успешно создан с сообщением
        - 400: Ошибки валидации
        """
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "Пользователь успешно зарегистрирован. Код подтверждения отправлен на email.",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(views.APIView):
    """
    API endpoint для подтверждения email.

    Подтверждает email пользователя путем валидации кода подтверждения, отправленного при регистрации.
    После подтверждения устанавливает флаг is_email_verified в True.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Подтверждение email пользователя",
        description="Подтверждение адреса электронной почты с использованием кода, отправленного при регистрации.",
        request=VerificationSerializer,
        responses={
            200: MessageResponseSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=["Аутентификация"],
    )
    def post(self, request):
        """
        Подтверждение адреса электронной почты с использованием кода подтверждения.

        Обязательные поля:
        - email: Email адрес для подтверждения
        - code: 6-значный код подтверждения (отправлен по email)

        Возвращает:
        - 200: Email успешно подтвержден
        - 400: Неверный или просроченный код
        - 404: Пользователь с указанным email не найден
        """
        serializer = VerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            code = serializer.validated_data["code"]

            try:
                user = User.objects.get(email=email)
                verification = Verification.objects.filter(
                    user=user, verification_type="email_token", code=code, is_used=False
                ).last()

                if verification and verification.is_valid():
                    verification.is_used = True
                    verification.save()

                    user.is_email_verified = True
                    user.save()

                    return Response(
                        {"message": "Email успешно подтвержден!"},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "Неверный или просроченный код."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            except User.DoesNotExist:
                return Response(
                    {"error": "Пользователь не найден."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Повторная отправка кода подтверждения email",
    description="Отправляет новый код подтверждения на email пользователя, если email еще не подтвержден.",
    request=ResendVerificationSerializer,
    responses={
        200: MessageResponseSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
    tags=["Аутентификация"],
)
class ResendVerificationEmailView(views.APIView):
    """
    API endpoint для повторной отправки письма с кодом подтверждения email.

    Позволяет пользователю получить новый код, если первый был потерян или не дошел.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.is_email_verified:
            return Response(
                {"error": "Email уже подтвержден."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Verification.objects.filter(
            user=user, verification_type="email_token", is_used=False
        ).update(is_used=True)

        otp_code = str(random.randint(100000, 999999))
        Verification.objects.create(
            user=user,
            verification_type="email_token",
            code=otp_code,
            expires_at=timezone.now() + timezone.timedelta(minutes=15),
        )
        send_verification_email.delay(user.email, otp_code)

        return Response(
            {"message": "Код подтверждения отправлен на email."},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    summary="Текущий профиль пользователя",
    description="Получение и обновление профиля авторизованного пользователя.",
    request=UserProfileSerializer,
    responses={200: UserProfileSerializer},
    tags=["Профиль"],
)
class CurrentUserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint для профиля текущего пользователя.

    Возвращает аккаунт и вложенные данные профиля. При отсутствии записи
    Profile создает ее автоматически.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        Profile.objects.get_or_create(user=self.request.user)
        return self.request.user


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access = response.data.pop("access")
            refresh = response.data.pop("refresh")
            set_auth_cookies(response, access, refresh)
            response.data = {"message": "Login successful"}
        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(REFRESH_COOKIE_NAME)
        if not refresh_token:
            return Response({"detail": "Refresh token not found"}, status=401)

        serializer = self.get_serializer(data={"refresh": refresh_token})
        serializer.is_valid(raise_exception=True)

        response = Response({"message": "Token refreshed"})
        set_auth_cookies(
            response,
            serializer.validated_data["access"],
            serializer.validated_data.get("refresh"),
        )
        return response


class LogoutView(views.APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Выход из системы",
        description="Удалить HttpOnly cookies access и refresh токенов пользователя.",
        responses={200: MessageResponseSerializer},
        tags=["Аутентификация"],
    )
    def post(self, request):
        response = Response({"message": "Logged out"})
        logout(request)
        clear_auth_cookies(response)
        return response
