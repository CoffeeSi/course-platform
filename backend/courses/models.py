from decimal import Decimal

from django.db import models
from django.conf import settings
from django.db.models import Max


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(
        max_length=255, unique=True, verbose_name="URL-идентификатор"
    )
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.name


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses_taught",
        verbose_name="Преподаватель",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
        verbose_name="Категория",
    )
    title = models.CharField(max_length=255, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание")

    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name="Цена"
    )

    is_published = models.BooleanField(default=False, verbose_name="Опубликован")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["instructor"]),
        ]

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="modules", verbose_name="Курс"
    )
    title = models.CharField(max_length=255, verbose_name="Название модуля")

    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")

    class Meta:
        verbose_name = "Модуль"
        verbose_name_plural = "Модули"
        ordering = ["order"]
        indexes = [
            models.Index(fields=["course"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    id = models.AutoField(primary_key=True)
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name="lessons", verbose_name="Модуль"
    )
    title = models.CharField(max_length=255, verbose_name="Название урока")
    content_text = models.TextField(blank=True, verbose_name="Текстовый контент")

    video_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Ссылка на видео",
        help_text="Введите S3 ключ объекта, например: videos/javascript_dom_lesson.mp4",
    )
    video_file = models.FileField(
        upload_to="videos/",
        blank=True,
        null=True,
        verbose_name="Видеофайл",
    )

    is_free = models.BooleanField(default=False, verbose_name="Бесплатный")

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок сортировки",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["order"]
        indexes = [
            models.Index(fields=["module"]),
            models.Index(fields=["title"]),
        ]

    def save(self, *args, **kwargs):
        if self.pk is None and not self.order:
            max_order = Lesson.objects.filter(module=self.module).aggregate(
                Max("order")
            )["order__max"]

            if max_order is not None:
                self.order = max_order + 1
            else:
                self.order = 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Урок {self.order}: {self.title}"

    @property
    def get_next_lesson_id(self):
        next_lesson = (
            Lesson.objects.filter(module=self.module, order__gt=self.order)
            .order_by("order")
            .first()
        )
        return next_lesson.id if next_lesson else None

    @property
    def get_prev_lesson_id(self):
        prev_lesson = (
            Lesson.objects.filter(module=self.module, order__lt=self.order)
            .order_by("-order")
            .first()
        )
        return prev_lesson.id if prev_lesson else None
