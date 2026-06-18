from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.db import models
from users.models import User
from .models import Category, Course, Module, Lesson
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    CourseDetailSerializer,
    ModuleSerializer,
    LessonSerializer,
)
from .permissions import (
    IsAdminOrReadOnly,
    IsCourseInstructorOrReadOnly,
    IsModuleInstructorOrReadOnly,
    IsLessonInstructorOrReadOnly,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint для управления категориями курсов.

    Позволяет администраторам создавать, редактировать и удалять категории.
    Все пользователи могут просматривать список категорий.

    Доступные действия:
    - GET /api/v1/courses/categories/ - получить список всех категорий
    - POST /api/v1/courses/categories/ - создать новую категорию (только для админов)
    - GET /api/v1/courses/categories/{id}/ - получить информацию о категории
    - PUT /api/v1/courses/categories/{id}/ - обновить категорию (только для админов)
    - DELETE /api/v1/courses/categories/{id}/ - удалить категорию (только для админов)
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        summary="Список категорий",
        description="Получить список всех категорий курсов",
        tags=["Категории"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Создать категорию",
        description="Создать новую категорию (только для администраторов)",
        tags=["Категории"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Получить категорию",
        description="Получить подробную информацию о категории",
        tags=["Категории"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Обновить категорию",
        description="Обновить информацию о категории (только для администраторов)",
        tags=["Категории"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Удалить категорию",
        description="Удалить категорию (только для администраторов)",
        tags=["Категории"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint для управления курсами.

    Преподаватели могут создавать и редактировать свои курсы.
    Администраторы могут редактировать все курсы.
    Все пользователи могут просматривать опубликованные курсы.

    Поддерживаемые параметры фильтрации:
    - category_id: фильтровать по ID категории
    - instructor_id: фильтровать по ID преподавателя

    Доступные действия:
    - GET /api/v1/courses/ - получить список курсов
    - POST /api/v1/courses/ - создать новый курс (только для преподавателей и админов)
    - GET /api/v1/courses/{id}/ - получить информацию о курсе с модулями
    - PUT /api/v1/courses/{id}/ - обновить курс (автор или админ)
    - DELETE /api/v1/courses/{id}/ - удалить курс (автор или админ)
    """

    permission_classes = [IsCourseInstructorOrReadOnly]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == User.Role.ADMIN or user.is_staff:
                queryset = Course.objects.all()
            elif user.role == User.Role.INSTRUCTOR:
                queryset = Course.objects.filter(
                    models.Q(is_published=True) | models.Q(instructor=user)
                )
            else:
                queryset = Course.objects.filter(is_published=True)
        else:
            queryset = Course.objects.filter(is_published=True)

        category_id = self.request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        instructor_id = self.request.query_params.get("instructor_id")
        if instructor_id:
            queryset = queryset.filter(instructor_id=instructor_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    @extend_schema(
        summary="Список курсов",
        description="Получить список курсов. Может быть отфильтрован по категории или преподавателю.",
        tags=["Курсы"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Создать курс",
        description="Создать новый курс (только для преподавателей и администраторов)",
        tags=["Курсы"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Получить курс",
        description="Получить подробную информацию о курсе с модулями и уроками",
        tags=["Курсы"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Обновить курс",
        description="Обновить информацию о курсе (только автор или администратор)",
        tags=["Курсы"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Удалить курс",
        description="Удалить курс (только автор или администратор)",
        tags=["Курсы"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ModuleViewSet(viewsets.ModelViewSet):
    """
    API endpoint для управления модулями курсов.

    Преподаватели могут создавать и редактировать модули своих курсов.
    Администраторы могут редактировать все модули.
    Все пользователи могут просматривать модули опубликованных курсов.

    Обязательный параметр:
    - course: ID курса (обязателен при получении списка модулей)

    Доступные действия:
    - GET /api/v1/courses/modules/?course={id} - получить модули курса
    - POST /api/v1/courses/modules/ - создать новый модуль (только для преподавателей)
    - GET /api/v1/courses/modules/{id}/ - получить модуль с уроками
    - PUT /api/v1/courses/modules/{id}/ - обновить модуль (автор или админ)
    - DELETE /api/v1/courses/modules/{id}/ - удалить модуль (автор или админ)
    """

    permission_classes = [IsModuleInstructorOrReadOnly]
    serializer_class = ModuleSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == User.Role.ADMIN or user.is_staff:
                queryset = Module.objects.all()
            elif user.role == User.Role.INSTRUCTOR:
                queryset = Module.objects.filter(
                    models.Q(course__is_published=True)
                    | models.Q(course__instructor=user)
                )
            else:
                queryset = Module.objects.filter(course__is_published=True)
        else:
            queryset = Module.objects.filter(course__is_published=True)

        course_id = self.request.query_params.get("course")
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset

    @extend_schema(
        summary="Список модулей",
        description="Получить список модулей курса. Требуется параметр course",
        tags=["Модули"],
    )
    def list(self, request, *args, **kwargs):
        user = request.user
        is_admin = user.is_authenticated and (
            user.is_staff or user.role == User.Role.ADMIN
        )
        if not is_admin:
            if "course" not in request.query_params:
                return Response(
                    {
                        "detail": "Необходимо указать параметр запроса 'course' для получения списка модулей."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Создать модуль",
        description="Создать новый модуль в курсе (только для преподавателя курса)",
        tags=["Модули"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Получить модуль",
        description="Получить информацию о модуле с его уроками",
        tags=["Модули"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Обновить модуль",
        description="Обновить модуль (только преподаватель или администратор)",
        tags=["Модули"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Удалить модуль",
        description="Удалить модуль (только преподаватель или администратор)",
        tags=["Модули"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class LessonViewSet(viewsets.ModelViewSet):
    """
    API endpoint для управления уроками.

    Преподаватели могут создавать и редактировать уроки своих курсов.
    Администраторы могут редактировать все уроки.
    Все пользователи могут просматривать уроки опубликованных курсов.

    Обязательный параметр:
    - module: ID модуля (обязателен при получении списка уроков)

    Доступные действия:
    - GET /api/v1/courses/lessons/?module={id} - получить уроки модуля
    - POST /api/v1/courses/lessons/ - создать новый урок (только для преподавателей)
    - GET /api/v1/courses/lessons/{id}/ - получить урок
    - PUT /api/v1/courses/lessons/{id}/ - обновить урок (автор или админ)
    - DELETE /api/v1/courses/lessons/{id}/ - удалить урок (автор или админ)
    """

    permission_classes = [IsLessonInstructorOrReadOnly]
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == User.Role.ADMIN or user.is_staff:
                queryset = Lesson.objects.all()
            elif user.role == User.Role.INSTRUCTOR:
                queryset = Lesson.objects.filter(
                    models.Q(module__course__is_published=True)
                    | models.Q(module__course__instructor=user)
                )
            else:
                queryset = Lesson.objects.filter(module__course__is_published=True)
        else:
            queryset = Lesson.objects.filter(module__course__is_published=True)

        module_id = self.request.query_params.get("module")
        if module_id:
            queryset = queryset.filter(module_id=module_id)

        return queryset

    @extend_schema(
        summary="Список уроков",
        description="Получить список уроков модуля. Требуется параметр module",
        tags=["Уроки"],
    )
    def list(self, request, *args, **kwargs):
        user = request.user
        is_admin = user.is_authenticated and (
            user.is_staff or user.role == User.Role.ADMIN
        )
        if not is_admin:
            if "module" not in request.query_params:
                return Response(
                    {
                        "detail": "Необходимо указать параметр запроса 'module' для получения списка уроков."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Создать урок",
        description="Создать новый урок в модуле (только для преподавателя курса)",
        tags=["Уроки"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Получить урок",
        description="Получить информацию об уроке",
        tags=["Уроки"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Обновить урок",
        description="Обновить урок (только преподаватель или администратор)",
        tags=["Уроки"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Удалить урок",
        description="Удалить урок (только преподаватель или администратор)",
        tags=["Уроки"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
