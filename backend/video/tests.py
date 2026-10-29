from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient

from courses.models import Category, Course, Module, Lesson
from enrollments.models import Enrollment, Progress
from users.models import User


class VideoURLViewTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="student@example.com", password="StrongPass123!"
        )
        self.student.is_email_verified = True
        self.student.save()

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
            price=0,
            is_published=True,
        )

        self.module = Module.objects.create(course=self.course, title="Basics", order=1)

        self.lesson = Lesson.objects.create(
            module=self.module,
            title="Video Lesson",
            content_text="Watch this lesson",
            video_url="videos/lesson.mp4",
            order=1,
        )

        self.enrollment = Enrollment.objects.create(
            student=self.student, course=self.course
        )

        self.progress = Progress.objects.create(
            enrollment=self.enrollment, lesson=self.lesson
        )

        self.client = APIClient()

    @patch("video.views.boto3.client")
    def test_video_url_request_marks_progress_complete(self, mock_boto_client):
        mock_s3 = mock_boto_client.return_value
        mock_s3.generate_presigned_url.return_value = "https://example.com/video.mp4"

        self.client.force_authenticate(user=self.student)
        response = self.client.get(
            reverse("video-url"),
            {"key": self.lesson.video_url},
        )

        self.assertEqual(response.status_code, 200)
        self.progress.refresh_from_db()
        self.assertTrue(self.progress.is_completed)
        self.assertIsNotNone(self.progress.completed_at)
