from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from users.tasks import send_verification_email
from .models import User, Profile, Verification
import random
from django.utils import timezone


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор информации профиля пользователя.

    Содержит личную информацию: имя, фамилию и URL аватара.
    Все поля опциональны.
    """

    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "avatar"]


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор текущего профиля пользователя.

    Возвращает данные аккаунта и вложенный профиль, а также позволяет
    обновлять поля профиля через PATCH/PUT.
    """

    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone_number",
            "role",
            "is_email_verified",
            "is_phone_verified",
            "profile",
        ]
        read_only_fields = [
            "id",
            "email",
            "phone_number",
            "role",
            "is_email_verified",
            "is_phone_verified",
        ]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)

        if profile_data is not None:
            profile, _ = Profile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        instance.refresh_from_db()
        return instance


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя.

    Валидирует и создает новый аккаунт пользователя. Пароль автоматически хешируется.
    Email должен быть уникален. Номер телефона опционален.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        help_text="Надежный пароль (минимум 8 символов, должен содержать цифры и буквы)",
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Подтверждение пароля (должно совпадать с полем password)",
    )

    class Meta:
        model = User
        fields = ["email", "phone_number", "password", "password_confirm"]
        extra_kwargs = {
            "email": {"help_text": "Email адрес пользователя (должен быть уникален)"},
            "phone_number": {
                "help_text": "Номер телефона (опционально, должен быть уникален, если указан)"
            },
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            phone_number=validated_data.get("phone_number"),
            role="student",
        )
        Profile.objects.create(user=user)

        otp_code = str(random.randint(100000, 999999))
        Verification.objects.create(
            user=user,
            verification_type="email_token",
            code=otp_code,
            expires_at=timezone.now() + timezone.timedelta(minutes=15),
        )
        send_verification_email.delay(user.email, otp_code)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ответа профиля пользователя.

    Возвращает информацию об аккаунте пользователя включая email, телефон, роль и детали профиля.
    """

    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone_number",
            "role",
            "is_email_verified",
            "is_phone_verified",
            "profile",
        ]
        extra_kwargs = {
            "id": {"help_text": "Уникальный идентификатор пользователя"},
            "email": {"help_text": "Email адрес пользователя"},
            "phone_number": {"help_text": "Номер телефона пользователя (опционально)"},
            "role": {
                "help_text": "Роль пользователя: student (студент), instructor (преподаватель) или admin (администратор)"
            },
            "is_email_verified": {"help_text": "Подтвержден ли email"},
            "is_phone_verified": {"help_text": "Подтвержден ли номер телефона"},
        }


class VerificationSerializer(serializers.Serializer):
    """
    Сериализатор для подтверждения email.

    Принимает email и код подтверждения для подтверждения email адреса пользователя.
    Код - это 6-значное число, отправленное на email пользователя при регистрации.
    """

    email = serializers.EmailField(
        required=True, help_text="Email адрес пользователя для подтверждения"
    )
    code = serializers.CharField(
        required=True,
        max_length=6,
        help_text="6-значный код подтверждения, отправленный на email",
    )


class ResendVerificationSerializer(serializers.Serializer):
    """
    Сериализатор для повторной отправки письма подтверждения email.

    Принимает только email пользователя.
    """

    email = serializers.EmailField(
        required=True, help_text="Email адрес пользователя для повторной отправки кода"
    )
