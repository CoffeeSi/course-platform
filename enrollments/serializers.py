from rest_framework import serializers
from django.utils import timezone
from .models import Enrollment, Progress
from courses.models import Course, Lesson
from courses.serializers import CourseSerializer, LessonSerializer


class ProgressSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отслеживания прогресса студента по урокам.
    """

    lesson_details = LessonSerializer(source="lesson", read_only=True)

    class Meta:
        model = Progress
        fields = [
            "id",
            "enrollment",
            "lesson",
            "lesson_details",
            "is_completed",
            "completed_at",
        ]
        read_only_fields = ["enrollment", "completed_at"]

    def update(self, instance, validated_data):
        """При завершении урока автоматически устанавливается completed_at."""
        is_completed = validated_data.get("is_completed", instance.is_completed)

        if is_completed and not instance.is_completed:
            instance.completed_at = timezone.now()

        instance.is_completed = is_completed
        instance.save()
        return instance


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для управления зачислениями студентов на курсы.
    """

    course_details = CourseSerializer(source="course", read_only=True)
    progress = ProgressSerializer(many=True, read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "course",
            "course_details",
            "progress",
            "enrolled_at",
        ]
        read_only_fields = ["student", "enrolled_at", "progress"]

    def create(self, validated_data):
        """При создании зачисления автоматически добавляется текущий пользователь как студент."""
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания зачисления (POST запрос).
    """

    class Meta:
        model = Enrollment
        fields = ["id", "course", "enrolled_at"]
        read_only_fields = ["id", "enrolled_at"]

    def validate_course(self, course):
        """Prevent duplicate enrollment before the database constraint is hit."""
        user = self.context["request"].user
        if Enrollment.objects.filter(student=user, course=course).exists():
            raise serializers.ValidationError("You are already enrolled in this course.")
        return course

    def create(self, validated_data):
        """При создании зачисления автоматически добавляется текущий пользователь как студент."""
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)
