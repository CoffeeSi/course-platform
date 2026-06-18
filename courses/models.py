from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL-идентификатор")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name


class Course(models.Model):
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='courses_taught',
        verbose_name="Преподаватель"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='courses',
        verbose_name="Категория"
    )
    title = models.CharField(max_length=255, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание")
    
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Цена") 
    
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='modules',
        verbose_name="Курс"
    )
    title = models.CharField(max_length=255, verbose_name="Название модуля")
    
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")

    class Meta:
        verbose_name = "Модуль"
        verbose_name_plural = "Модули"
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(
        Module, 
        on_delete=models.CASCADE, 
        related_name='lessons',
        verbose_name="Модуль"
    )
    title = models.CharField(max_length=255, verbose_name="Название урока")
    content_text = models.TextField(blank=True, verbose_name="Текстовый контент")
    
    video_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на видео")
    video_file = models.FileField(
        upload_to="videos/",
        blank=True,
        null=True,
        verbose_name="Видеофайл",
    )
    
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['order']

    def __str__(self):
        return f"Урок {self.order}: {self.title}"