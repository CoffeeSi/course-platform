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


class CourseShortSerializer(serializers.ModelSerializer):
    """Краткий курс для вложенности внутри модуля, чтобы не тянуть преподавателя и категорию снова"""

    class Meta:
        model = Course
        fields = ["id", "title", "price", "is_published"]


class ModuleShortSerializer(serializers.ModelSerializer):
    """Краткий модуль для вложенности внутри урока, чтобы не тянуть уроки обратно"""

    course_detail = CourseShortSerializer(source="course", read_only=True)

    class Meta:
        model = Module
        fields = ["id", "title", "course", "course_detail", "order"]


class LessonShortSerializer(serializers.ModelSerializer):
    """Краткий урок для вложенности внутри модуля (без деталей модуля)"""

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "content_text",
            "video_url",
            "video_file",
            "order",
            "is_free",
            "created_at",
        ]


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


class ModuleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модуля курса.

    Содержит информацию о модуле и список всех уроков в модуле.
    """

    lessons = serializers.SerializerMethodField()
    course_detail = CourseSerializer(source="course", read_only=True)

    class Meta:
        model = Module
        fields = ["id", "course", "course_detail", "title", "order", "lessons"]
        extra_kwargs = {
            "id": {"help_text": "Уникальный идентификатор модуля"},
            "course": {"help_text": "Курс, которому принадлежит модуль"},
            "course_detail": {
                "help_text": "Информация о курсе, которому принадлежит модуль"
            },
            "title": {"help_text": "Название модуля"},
            "order": {"help_text": "Порядок сортировки в курсе"},
            "lessons": {"help_text": "Список всех уроков в модуле"},
        }

    def get_lessons(self, obj):
        request = self.context.get("request")
        if getattr(request, "user", None) is None:
            return LessonShortSerializer(obj.lessons.all(), many=True).data

        user = request.user

        if not user.is_authenticated:
            free_lessons = obj.lessons.filter(is_free=True)
            return LessonShortSerializer(free_lessons, many=True).data

        if user.is_staff or user.role == User.Role.ADMIN:
            return LessonShortSerializer(obj.lessons.all(), many=True).data

        if obj.course.instructor_id == user.id:
            return LessonShortSerializer(obj.lessons.all(), many=True).data

        if Enrollment.objects.filter(
            student_id=user.id, course_id=obj.course_id
        ).exists():
            return LessonShortSerializer(obj.lessons.all(), many=True).data

        free_lessons = obj.lessons.filter(is_free=True)
        return LessonShortSerializer(free_lessons, many=True).data

    def validate_course(self, value):
        request = self.context.get("request")
        if not request or not request.user:
            return value

        user = request.user
        if (
            user.role != User.Role.ADMIN
            and not user.is_staff
            and value.instructor_id != user.id
        ):
            raise serializers.ValidationError(
                "Вы не можете добавлять модули в этот курс, так как не являетесь его преподавателем."
            )
        return value


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для урока.

    Содержит информацию об уроке: название, текстовый контент, ссылку на видео или видеофайл.
    """

    module_detail = ModuleShortSerializer(source="module", read_only=True)
    next_lesson_id = serializers.ReadOnlyField(source="get_next_lesson_id")
    prev_lesson_id = serializers.ReadOnlyField(source="get_prev_lesson_id")

    class Meta:
        model = Lesson
        fields = [
            "id",
            "module",
            "module_detail",
            "title",
            "content_text",
            "video_url",
            "video_file",
            "order",
            "next_lesson_id",
            "prev_lesson_id",
            "is_free",
            "created_at",
        ]
        extra_kwargs = {
            "id": {"help_text": "Уникальный идентификатор урока"},
            "module": {"help_text": "Модуль, которому принадлежит урок"},
            "module_detail": {
                "help_text": "Информация о модуле, которому принадлежит урок"
            },
            "title": {"help_text": "Название урока"},
            "content_text": {"help_text": "Текстовый контент урока (опционально)"},
            "video_url": {"help_text": "Ссылка на видео (YouTube, Vimeo и т.д.)"},
            "video_file": {"help_text": "Загруженный видеофайл"},
            "prev_lesson_id": {"help_text": "Идентификатор предыдущего урока"},
            "next_lesson_id": {"help_text": "Идентификатор следующего урока"},
            "order": {"help_text": "Порядок сортировки в модуле"},
            "is_free": {"help_text": "Флаг бесплатного урока"},
            "created_at": {"help_text": "Дата создания урока"},
        }

    def validate_module(self, value):
        request = self.context.get("request")
        if not request or not request.user:
            return value

        user = request.user
        if (
            user.role != User.Role.ADMIN
            and not user.is_staff
            and value.course.instructor_id != user.id
        ):
            raise serializers.ValidationError(
                "Вы не можете добавлять уроки в этот модуль, так как не являетесь преподавателем курса."
            )
        return value


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
