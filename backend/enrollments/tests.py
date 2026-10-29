from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from users.models import User, Verification
from courses.models import Course, Category, Module, Lesson
from .models import Enrollment, Progress


class EnrollmentTestCase(APITestCase):
    """Тесты для управления зачислениями на курсы."""

    def setUp(self):
        """Подготовка данных для тестов."""
        self.student = User.objects.create_user(
            email="student@example.com", password="StrongPass123!"
        )
        self.student.is_email_verified = True
        self.student.save()

        self.instructor = User.objects.create_user(
            email="instructor@example.com", password="StrongPass123!"
        )
        self.instructor.is_email_verified = True
        self.instructor.role = "instructor"
        self.instructor.save()

        self.category = Category.objects.create(
            name="Python", slug="python", description="Python курсы"
        )

        self.course = Course.objects.create(
            instructor=self.instructor,
            category=self.category,
            title="Python для начинающих",
            description="Введение в Python",
            price=99.99,
            is_published=True,
        )

        self.module = Module.objects.create(
            course=self.course, title="Основы Python", order=1
        )

        self.lesson = Lesson.objects.create(
            module=self.module,
            title="Переменные и типы данных",
            content_text="Урок о переменных",
            order=1,
        )

        self.client = APIClient()

    def test_student_can_enroll_in_course(self):
        """Тест: студент может записаться на курс."""
        self.client.force_authenticate(user=self.student)

        response = self.client.post(
            reverse("enrollment-list-create"), {"course": self.course.id}, format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Enrollment.objects.filter(student=self.student, course=self.course).exists()
        )

    def test_student_cannot_enroll_twice_in_same_course(self):
        """Тест: студент не может дважды записаться на один курс."""
        self.client.force_authenticate(user=self.student)

        response1 = self.client.post(
            reverse("enrollment-list-create"), {"course": self.course.id}, format="json"
        )
        self.assertEqual(response1.status_code, 201)

        response2 = self.client.post(
            reverse("enrollment-list-create"), {"course": self.course.id}, format="json"
        )
        self.assertEqual(response2.status_code, 400)

    def test_student_can_see_only_own_enrollments(self):
        """Тест: студент видит только свои зачисления."""
        other_student = User.objects.create_user(
            email="other@example.com", password="StrongPass123!"
        )
        other_student.is_email_verified = True
        other_student.save()

        enrollment1 = Enrollment.objects.create(
            student=self.student, course=self.course
        )
        enrollment2 = Enrollment.objects.create(
            student=other_student, course=self.course
        )

        self.client.force_authenticate(user=self.student)
        response = self.client.get(reverse("enrollment-list-create"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], enrollment1.id)

    def test_student_can_delete_own_enrollment(self):
        """Тест: студент может удалить свое зачисление."""
        enrollment = Enrollment.objects.create(student=self.student, course=self.course)

        self.client.force_authenticate(user=self.student)
        response = self.client.delete(
            reverse("enrollment-detail", kwargs={"id": enrollment.id})
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Enrollment.objects.filter(id=enrollment.id).exists())

    def test_student_can_retrieve_own_enrollment(self):
        """Тест: студент может получить детали своего зачисления."""
        enrollment = Enrollment.objects.create(student=self.student, course=self.course)

        self.client.force_authenticate(user=self.student)
        response = self.client.get(
            reverse("enrollment-detail", kwargs={"id": enrollment.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], enrollment.id)
        self.assertEqual(response.data["course"], self.course.id)

    def test_student_cannot_delete_other_enrollment(self):
        """Тест: студент не может удалить чужое зачисление."""
        other_student = User.objects.create_user(
            email="other@example.com", password="StrongPass123!"
        )
        other_student.is_email_verified = True
        other_student.save()

        enrollment = Enrollment.objects.create(
            student=other_student, course=self.course
        )

        self.client.force_authenticate(user=self.student)
        response = self.client.delete(
            reverse("enrollment-detail", kwargs={"id": enrollment.id})
        )

        self.assertEqual(response.status_code, 403)


class ProgressTestCase(APITestCase):
    """Тесты для отслеживания прогресса студентов."""

    def setUp(self):
        """Подготовка данных для тестов."""
        self.student = User.objects.create_user(
            email="student@example.com", password="StrongPass123!"
        )
        self.student.is_email_verified = True
        self.student.save()

        self.instructor = User.objects.create_user(
            email="instructor@example.com", password="StrongPass123!"
        )
        self.instructor.is_email_verified = True
        self.instructor.role = "instructor"
        self.instructor.save()

        self.category = Category.objects.create(
            name="Python", slug="python", description="Python курсы"
        )

        self.course = Course.objects.create(
            instructor=self.instructor,
            category=self.category,
            title="Python для начинающих",
            description="Введение в Python",
            price=99.99,
            is_published=True,
        )

        self.module = Module.objects.create(
            course=self.course, title="Основы Python", order=1
        )

        self.lesson = Lesson.objects.create(
            module=self.module,
            title="Переменные и типы данных",
            content_text="Урок о переменных",
            order=1,
        )

        self.enrollment = Enrollment.objects.create(
            student=self.student, course=self.course
        )

        self.progress = Progress.objects.create(
            enrollment=self.enrollment, lesson=self.lesson
        )

        self.client = APIClient()

    def test_student_can_mark_lesson_as_complete(self):
        """Тест: студент может отметить урок как завершенный."""
        self.client.force_authenticate(user=self.student)

        response = self.client.post(
            reverse("progress-mark-complete", kwargs={"id": self.progress.id})
        )

        self.assertEqual(response.status_code, 200)
        self.progress.refresh_from_db()
        self.assertTrue(self.progress.is_completed)
        self.assertIsNotNone(self.progress.completed_at)

    def test_student_can_mark_lesson_as_incomplete(self):
        """Тест: студент может отметить урок как незавершенный."""
        self.progress.is_completed = True
        self.progress.completed_at = timezone.now()
        self.progress.save()

        self.client.force_authenticate(user=self.student)

        response = self.client.post(
            reverse("progress-mark-incomplete", kwargs={"id": self.progress.id})
        )

        self.assertEqual(response.status_code, 200)
        self.progress.refresh_from_db()
        self.assertFalse(self.progress.is_completed)
        self.assertIsNone(self.progress.completed_at)

    def test_student_can_retrieve_and_update_own_progress(self):
        """Тест: студент может получить и обновить свой прогресс."""
        self.client.force_authenticate(user=self.student)

        detail_response = self.client.get(
            reverse("progress-detail", kwargs={"id": self.progress.id})
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.data["id"], self.progress.id)

        update_response = self.client.patch(
            reverse("progress-detail", kwargs={"id": self.progress.id}),
            {"is_completed": True},
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)

        self.progress.refresh_from_db()
        self.assertTrue(self.progress.is_completed)
        self.assertIsNotNone(self.progress.completed_at)

    def test_student_can_only_see_own_progress(self):
        """Тест: студент видит только свой прогресс."""
        other_student = User.objects.create_user(
            email="other@example.com", password="StrongPass123!"
        )
        other_student.is_email_verified = True
        other_student.save()

        other_enrollment = Enrollment.objects.create(
            student=other_student, course=self.course
        )
        other_progress = Progress.objects.create(
            enrollment=other_enrollment, lesson=self.lesson
        )

        self.client.force_authenticate(user=self.student)
        response = self.client.get(reverse("progress-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.progress.id)
