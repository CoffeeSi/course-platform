from rest_framework import serializers
from users.models import User
from users.serializers import UserSerializer
from .models import Category, Course, Module, Lesson
from enrollments.models import Enrollment


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для категории курсов.

    Содержит информацию о категории: название, URL-идентификатор и описание.
    """

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]
        extra_kwargs = {
            "id": {"help_text": "Уникальный идентификатор категории"},
            "name": {"help_text": "Название категории"},
            "slug": {"help_text": "URL-идентификатор категории (уникален)"},
            "description": {"help_text": "Описание категории (опционально)"},
        }


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для урока.

    Содержит информацию об уроке: название, текстовый контент, ссылку на видео или видеофайл.
    """

    class Meta:
        model = Lesson
        fields = [
            "id",
            "module",
            "title",
            "content_text",
            "video_url",
            "video_file",
            "order",
            "is_free",
            "created_at",
        ]
        extra_kwargs = {
            "id": {"help_text": "Уникальный идентификатор урока"},
            "module": {"help_text": "ID модуля, которому принадлежит урок"},
            "title": {"help_text": "Название урока"},
            "content_text": {"help_text": "Текстовый контент урока (опционально)"},
            "video_url": {"help_text": "Ссылка на видео (YouTube, Vimeo и т.д.)"},
            "video_file": {"help_text": "Загруженный видеофайл"},
            "order": {"help_text": "Порядок сортировки в модуле"},
            "is_free": {"help_text": "Флаг бесплатного урока"},
            "created_at": {"help_text": "Дата создания урока"},
        }

    def validate_module(self, value):
        user = self.context["request"].user
        if (
            user.role != User.Role.ADMIN
            and not user.is_staff
            and value.course.instructor != user
        ):
            raise serializers.ValidationError(
                "Вы не можете добавлять уроки в этот модуль, так как не являетесь преподавателем курса."
            )
        return value


class ModuleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модуля курса.

    Содержит информацию о модуле и список всех уроков в модуле.
    """

    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ["id", "course", "title", "order", "lessons"]
        extra_kwargs = {
            "id": {"help_text": "Уникальный идентификатор модуля"},
            "course": {"help_text": "ID курса, которому принадлежит модуль"},
            "title": {"help_text": "Название модуля"},
            "order": {"help_text": "Порядок сортировки в курсе"},
            "lessons": {"help_text": "Список всех уроков в модуле"},
        }

    def get_lessons(self, obj):
        request = self.context["request"]
        user = request.user

        if not request or not user.is_authenticated:
            return []

        if user.is_staff or user.role == User.Role.ADMIN:
            return LessonSerializer(obj.lessons.all(), many=True).data

        if obj.course.instructor == user:
            return LessonSerializer(obj.lessons.all(), many=True).data

        if Enrollment.objects.filter(student=user, course=obj.course).exists():
            return LessonSerializer(obj.lessons.all(), many=True).data

        free_lessons = obj.lessons.filter(is_free=True)
        return LessonSerializer(free_lessons, many=True).data

    def validate_course(self, value):
        user = self.context["request"].user
        if (
            user.role != User.Role.ADMIN
            and not user.is_staff
            and value.instructor != user
        ):
            raise serializers.ValidationError(
                "Вы не можете добавлять модули в этот курс, так как не являетесь его преподавателем."
            )
        return value

    def validate_is_free(self, value):
        if value.is_free == False:
            raise serializers.ValidationError("Урок не может быть бесплатным.")
        return value


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для курса (краткий вид).

    Содержит основную информацию о курсе без деталей о модулях.
    Используется для списка курсов и при создании/обновлении курса.
    """

    instructor = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "instructor",
            "category",
            "category_id",
            "title",
            "description",
            "price",
            "is_published",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "id": {"help_text": "Уникальный идентификатор курса"},
            "instructor": {"help_text": "Информация о преподавателе"},
            "category": {"help_text": "Информация о категории"},
            "category_id": {"help_text": "ID категории (для создания/обновления)"},
            "title": {"help_text": "Название курса"},
            "description": {"help_text": "Описание курса"},
            "price": {"help_text": "Цена курса"},
            "is_published": {"help_text": "Опубликован ли курс"},
            "created_at": {"help_text": "Дата создания"},
            "updated_at": {"help_text": "Дата последнего обновления"},
        }


class CourseDetailSerializer(CourseSerializer):
    """
    Сериализатор для детального вида курса.

    Содержит полную информацию о курсе включая все модули и уроки.
    Используется при получении информации о конкретном курсе.
    """

    modules = ModuleSerializer(many=True, read_only=True)

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ["modules"]
        extra_kwargs = CourseSerializer.Meta.extra_kwargs
        extra_kwargs.update(
            {
                "modules": {"help_text": "Список всех модулей курса"},
            }
        )
