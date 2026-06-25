from rest_framework import generics, status, viewsets
from rest_framework.decorators import APIView, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from django.db.models import QuerySet
from django.utils import timezone

from courses.models import Lesson

from .models import Enrollment, Progress
from .serializers import (
    EnrollmentSerializer,
    EnrollmentCreateSerializer,
    ProgressSerializer,
)
from .permissions import IsEnrollmentOwner
from users.permissions import IsEmailVerified


@extend_schema(
    summary="Мои зачисления на курсы",
    description="Получение списка курсов, на которые зачислен текущий пользователь, и создание нового зачисления.",
    tags=["Зачисления"],
)
class EnrollmentListCreateView(generics.ListCreateAPIView):
    """
    API endpoint для управления зачислениями текущего пользователя.

    GET - получить список всех зачислений пользователя
    POST - зачислиться на новый курс
    """

    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def get_serializer_class(self) -> type:
        """Используем разные сериализаторы для GET и POST."""
        if self.request.method == "POST":
            return EnrollmentCreateSerializer
        return EnrollmentSerializer

    def get_queryset(self):
        """Возвращаем только зачисления текущего пользователя."""
        return Enrollment.objects.filter(student=self.request.user).prefetch_related(
            "progresses"
        )

    def perform_create(self, serializer):
        """Автоматически устанавливаем текущего пользователя как студента."""
        serializer.save(student=self.request.user)

    @extend_schema(
        summary="Получить прогресс по курсу",
        description="Получить список пройденных и непройденных уроков в курсе.",
        responses={
            200: OpenApiExample(
                "Успешно",
                value={
                    "id": 1,
                    "course": 1,
                    "progresses": [
                        {
                            "id": 1,
                            "lesson": 1,
                            "is_completed": True,
                            "completed_at": "2026-06-19T12:00:00Z",
                        },
                        {
                            "id": 2,
                            "lesson": 2,
                            "is_completed": False,
                            "completed_at": None,
                        },
                    ],
                },
            )
        },
        tags=["Зачисления"],
    )
    @action(detail=False, methods=["get"])
    def progress(self, request):
        """Получить прогресс по всем курсам."""
        enrollments = self.get_queryset()
        data = []
        for enrollment in enrollments:
            data.append(
                {
                    "enrollment_id": enrollment.id,
                    "course": enrollment.course.id,
                    "course_title": enrollment.course.title,
                    "progresses": ProgressSerializer(
                        enrollment.progresses.all(), many=True
                    ).data,
                }
            )
        return Response(data)


@extend_schema(
    summary="Деталь зачисления",
    description="Получить детальную информацию о зачислении на курс и удалить зачисление.",
    tags=["Зачисления"],
)
class EnrollmentDetailView(generics.RetrieveDestroyAPIView):
    """
    API endpoint для управления конкретным зачислением.

    GET - получить детали зачисления
    DELETE - отписаться от курса (удалить зачисление)
    """

    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified, IsEnrollmentOwner]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[Enrollment]:
        """Return all enrollments so object permissions can produce 403."""
        return Enrollment.objects.prefetch_related("progresses")


class CheckCourseStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id: int):
        user = request.user

        enrollment = Enrollment.objects.filter(
            student=user, course_id=course_id
        ).first()
        is_enrolled = bool(enrollment)

        progress_percent = 0
        if is_enrolled:
            total_lessons = Lesson.objects.filter(module__course_id=course_id).count()

            if total_lessons > 0:
                completed_lessons = Progress.objects.filter(
                    enrollment=enrollment,
                    is_completed=True,
                ).count()
                progress_percent = int((completed_lessons / total_lessons) * 100)
            else:
                progress_percent = 0

        return Response(
            {
                "course_id": int(course_id),
                "is_enrolled": is_enrolled,
                "progress_percent": progress_percent,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    summary="Отслеживание прогресса",
    description="Получение и обновление статуса завершения уроков.",
    tags=["Прогресс"],
)
class ProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления прогрессом студента по урокам.
    """

    serializer_class = ProgressSerializer
    queryset = Progress.objects.none()
    permission_classes = [IsAuthenticated, IsEmailVerified]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[Progress]:
        """Возвращаем только прогресс для зачислений текущего пользователя."""
        return Progress.objects.filter(
            enrollment__student=self.request.user
        ).select_related("enrollment", "lesson")

    def perform_update(self, serializer):
        """Обновляем прогресс с автоматической установкой времени завершения."""
        serializer.save()

    @extend_schema(
        summary="Отметить урок как завершенный",
        description="Отметить конкретный урок как завершенный.",
        request=None,
        parameters=[
            OpenApiParameter(
                "id",
                OpenApiTypes.INT,
                OpenApiParameter.PATH,
                description="Progress ID",
            )
        ],
        responses={200: ProgressSerializer},
        tags=["Прогресс"],
    )
    @action(detail=True, methods=["post"])
    def mark_complete(self, request, id=None):
        """Отметить урок как завершенный."""
        progress = self.get_object()
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()
        serializer = self.get_serializer(progress)
        return Response(serializer.data)

    @extend_schema(
        summary="Отметить урок как незавершенный",
        description="Отметить конкретный урок как незавершенный.",
        request=None,
        parameters=[
            OpenApiParameter(
                "id",
                OpenApiTypes.INT,
                OpenApiParameter.PATH,
                description="Progress ID",
            )
        ],
        responses={200: ProgressSerializer},
        tags=["Прогресс"],
    )
    @action(detail=True, methods=["post"])
    def mark_incomplete(self, request, id=None):
        """Отметить урок как незавершенный."""
        progress = self.get_object()
        progress.is_completed = False
        progress.completed_at = None
        progress.save()
        serializer = self.get_serializer(progress)
        return Response(serializer.data)
