import boto3
from botocore.config import Config
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from urllib.parse import urlparse

from courses.models import Lesson
from enrollments.models import Enrollment, Progress

VideoUrlResponseSerializer = inline_serializer(
    name="VideoUrlResponse",
    fields={"url": serializers.CharField()},
)


class VideoURLView(APIView):
    permission_classes = [IsAuthenticated]

    def _resolve_lesson(self, lesson_id, video_key):
        queryset = Lesson.objects.select_related("module__course")

        if lesson_id:
            lesson = queryset.filter(id=lesson_id).first()
            if lesson:
                return lesson

        if video_key:
            return queryset.filter(
                Q(video_url=video_key) | Q(video_file=video_key)
            ).first()

        return None

    def _mark_lesson_progress(self, user, lesson):
        enrollment = Enrollment.objects.filter(
            student=user, course=lesson.module.course
        ).first()
        if not enrollment:
            return

        progress, created = Progress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={"is_completed": True, "completed_at": timezone.now()},
        )

        if created or not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save(update_fields=["is_completed", "completed_at"])

    @extend_schema(
        summary="Получить защищенную ссылку на видео",
        description="Сформировать временную подписанную ссылку на видеофайл по ключу объекта или по lesson_id.",
        parameters=[
            OpenApiParameter(
                name="key",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Ключ видеофайла или URL объекта хранения",
            ),
            OpenApiParameter(
                name="lesson_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID урока, для которого нужно отметить прогресс и найти видео",
            ),
        ],
        responses={200: VideoUrlResponseSerializer},
        tags=["Видео"],
    )
    def get(self, request):
        raw_video_key = request.query_params.get("key")
        if not raw_video_key:
            return Response({"error": "Key is required"}, status=400)

        parsed_url = urlparse(raw_video_key)
        video_key = parsed_url.path

        video_key = video_key.lstrip("/")

        bucket_prefix = f"{settings.AWS_STORAGE_BUCKET_NAME}/"
        if video_key.startswith(bucket_prefix):
            video_key = video_key[len(bucket_prefix) :]

        if video_key.startswith("api/v1/download-shared-object/"):
            video_key = video_key.replace("api/v1/download-shared-object/", "")

        lesson_id = request.query_params.get("lesson_id")
        lesson = self._resolve_lesson(lesson_id, video_key)
        if lesson:
            self._mark_lesson_progress(request.user, lesson)

        my_config = Config(signature_version="s3v4", s3={"addressing_style": "path"})

        s3 = boto3.client(
            "s3",
            endpoint_url=getattr(
                settings, "AWS_S3_PUBLIC_ENDPOINT_URL", settings.AWS_S3_ENDPOINT_URL
            ),
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=my_config,
        )

        try:
            url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": video_key},
                ExpiresIn=3600,
            )
            return Response({"url": url})
        except Exception as e:
            return Response(
                {"error": f"Failed to generate secure URL: {str(e)}"}, status=500
            )
