from rest_framework import status, views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import User, Verification
from .serializers import UserRegisterSerializer, VerificationSerializer


class RegisterView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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
    permission_classes = [AllowAny]

    def post(self, request):
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
