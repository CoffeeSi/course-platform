from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from users.models import User, Verification


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
