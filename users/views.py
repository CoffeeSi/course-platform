from rest_framework import status, views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from .models import User, Verification
from .serializers import UserRegisterSerializer, VerificationSerializer


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
            201: OpenApiExample(
                "Успешно",
                value={
                    "message": "Пользователь успешно зарегистрирован. Код подтверждения отправлен на email."
                },
            ),
            400: OpenApiExample(
                "Ошибка валидации",
                value={
                    "email": ["Email уже зарегистрирован"],
                    "password": ["Пароль слишком простой"],
                },
            ),
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
            200: OpenApiExample(
                "Успешно",
                value={"message": "Email успешно подтвержден!"},
            ),
            400: OpenApiExample(
                "Неверный код",
                value={"error": "Неверный или просроченный код."},
            ),
            404: OpenApiExample(
                "Пользователь не найден",
                value={"error": "Пользователь не найден."},
            ),
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
