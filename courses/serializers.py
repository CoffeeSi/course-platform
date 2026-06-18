from rest_framework import serializers
from users.models import User
from users.serializers import UserSerializer
from .models import Category, Course, Module, Lesson


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

    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ["id", "course", "title", "order", "lessons"]
        extra_kwargs = {
            "id": {"help_text": "Уникальный идентификатор модуля"},
            "course": {"help_text": "ID курса, которому принадлежит модуль"},
            "title": {"help_text": "Название модуля"},
            "order": {"help_text": "Порядок сортировки в курсе"},
            "lessons": {"help_text": "Список уроков в модуле"},
        }

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


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детального вида курса.

    Содержит полную информацию о курсе включая все модули и уроки.
    Используется при получении информации о конкретном курсе.
    """

    instructor = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "instructor",
            "category",
            "title",
            "description",
            "price",
            "is_published",
            "modules",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "id": {"help_text": "Уникальный идентификатор курса"},
            "instructor": {"help_text": "Информация о преподавателе"},
            "category": {"help_text": "Информация о категории"},
            "title": {"help_text": "Название курса"},
            "description": {"help_text": "Описание курса"},
            "price": {"help_text": "Цена курса"},
            "is_published": {"help_text": "Опубликован ли курс"},
            "modules": {"help_text": "Список всех модулей курса"},
            "created_at": {"help_text": "Дата создания"},
            "updated_at": {"help_text": "Дата последнего обновления"},
        }
