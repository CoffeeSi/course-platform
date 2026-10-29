from django.urls import reverse
from rest_framework.test import APITestCase

from courses.models import Category, Course
from users.models import User
from payments.models import Payment


class PaymentAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="student@example.com", password="StrongPass123!"
        )
        self.user.is_email_verified = True
        self.user.save()

        self.instructor = User.objects.create_user(
            email="instructor@example.com", password="StrongPass123!"
        )
        self.instructor.is_email_verified = True
        self.instructor.role = User.Role.INSTRUCTOR
        self.instructor.save()

        self.category = Category.objects.create(
            name="Python", slug="python", description="Python courses"
        )
        self.course = Course.objects.create(
            instructor=self.instructor,
            category=self.category,
            title="Python Basics",
            description="Intro course",
            price=49.99,
            is_published=True,
        )

    def test_payment_create_requires_authentication(self):
        response = self.client.post(
            reverse("payment-create"),
            {"course_id": self.course.id, "provider": "stripe"},
        )
        self.assertEqual(response.status_code, 401)

    def test_payment_create_builds_pending_payment(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("payment-create"),
            {"course_id": self.course.id, "provider": "stripe"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Payment.objects.count(), 1)
        payment = Payment.objects.first()
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.course, self.course)
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(response.data["payment"]["provider"], "stripe")
