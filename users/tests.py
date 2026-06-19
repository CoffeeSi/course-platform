from datetime import timedelta
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User, Verification, Profile


class VerifyEmailViewTests(APITestCase):
    def test_verify_email_marks_user_verified(self):
        user = User.objects.create_user(
            email="test@example.com", password="StrongPass123!"
        )
        Verification.objects.create(
            user=user,
            verification_type="email_token",
            code="123456",
            expires_at=timezone.now() + timedelta(minutes=15),
        )

        response = self.client.post(
            reverse("verify-email"),
            {"email": "test@example.com", "code": "123456"},
            format="json",
        )

        user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Email успешно подтвержден!")
        self.assertTrue(user.is_email_verified)

    def test_verify_email_rejects_expired_code(self):
        user = User.objects.create_user(
            email="expired@example.com", password="StrongPass123!"
        )
        Verification.objects.create(
            user=user,
            verification_type="email_token",
            code="654321",
            expires_at=timezone.now() - timedelta(minutes=1),
        )

        response = self.client.post(
            reverse("verify-email"),
            {"email": "expired@example.com", "code": "654321"},
            format="json",
        )

        user.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Неверный или просроченный код.")
        self.assertFalse(user.is_email_verified)


class ResendVerificationEmailViewTests(APITestCase):
    @patch("users.views.random.randint", return_value=123456)
    @patch("users.views.send_verification_email.delay")
    def test_resend_email_verification_creates_new_code(self, mock_send, _mock_randint):
        user = User.objects.create_user(
            email="resend@example.com", password="StrongPass123!"
        )

        old_verification = Verification.objects.create(
            user=user,
            verification_type="email_token",
            code="111111",
            expires_at=timezone.now() - timedelta(minutes=1),
        )

        response = self.client.post(
            reverse("resend-email-verification"),
            {"email": "resend@example.com"},
            format="json",
        )

        new_verification = Verification.objects.filter(
            user=user, verification_type="email_token"
        ).latest("created_at")

        old_verification.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Код подтверждения отправлен на email.")
        self.assertTrue(old_verification.is_used)
        self.assertEqual(new_verification.code, "123456")
        self.assertFalse(new_verification.is_used)
        mock_send.assert_called_once_with("resend@example.com", "123456")

    def test_resend_email_verification_rejects_verified_user(self):
        user = User.objects.create_user(
            email="verified@example.com", password="StrongPass123!"
        )
        user.is_email_verified = True
        user.save()

        response = self.client.post(
            reverse("resend-email-verification"),
            {"email": "verified@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Email уже подтвержден.")


class CurrentUserProfileViewTests(APITestCase):
    def test_profile_get_creates_missing_profile(self):
        user = User.objects.create_user(
            email="profile@example.com", password="StrongPass123!"
        )
        user.is_email_verified = True
        user.save()

        self.client.force_authenticate(user=user)

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "profile@example.com")
        self.assertEqual(response.data["profile"]["first_name"], "")
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_profile_patch_updates_profile_fields(self):
        user = User.objects.create_user(
            email="update@example.com", password="StrongPass123!"
        )
        user.is_email_verified = True
        user.save()
        Profile.objects.create(user=user)

        self.client.force_authenticate(user=user)

        response = self.client.patch(
            reverse("profile"),
            {
                "profile": {
                    "first_name": "Ivan",
                    "last_name": "Petrov",
                    "avatar": "https://example.com/avatar.png",
                }
            },
            format="json",
        )

        profile = Profile.objects.get(user=user)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(profile.first_name, "Ivan")
        self.assertEqual(profile.last_name, "Petrov")
        self.assertEqual(profile.avatar, "https://example.com/avatar.png")
        self.assertEqual(response.data["profile"]["first_name"], "Ivan")


class UserEndpointSmokeTests(APITestCase):
    @patch("users.serializers.random.randint", return_value=123456)
    @patch("users.serializers.send_verification_email.delay")
    def test_register_login_refresh_and_schema_endpoints(self, mock_send, _mock_randint):
        register_response = self.client.post(
            reverse("register"),
            {
                "email": "new-user@example.com",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            },
            format="json",
        )
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        mock_send.assert_called_once_with("new-user@example.com", "123456")

        user = User.objects.get(email="new-user@example.com")
        user.is_email_verified = True
        user.save()

        login_response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": "new-user@example.com", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)

        refresh_response = self.client.post(
            reverse("token_refresh"),
            {"refresh": login_response.data["refresh"]},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

        schema_response = self.client.get(reverse("schema"))
        self.assertEqual(schema_response.status_code, status.HTTP_200_OK)

        swagger_response = self.client.get(reverse("swagger-ui"))
        self.assertEqual(swagger_response.status_code, status.HTTP_200_OK)

        redoc_response = self.client.get(reverse("redoc"))
        self.assertEqual(redoc_response.status_code, status.HTTP_200_OK)
