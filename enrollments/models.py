from django.db import models
from django.conf import settings
from courses.models import Course, Lesson


class Enrollment(models.Model):
    """
    Модель зачисления/покупки студентом курса.

    Представляет связь между студентом и курсом.
    Уникальная пара (student, course) обеспечивает, что студент
    не сможет дважды зачислиться на один и тот же курс.
    """

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Студент",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Курс",
    )
    enrolled_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата зачисления"
    )

    progresses = models.ManyToManyField(
        Lesson,
        through="Progress",
        related_name="enrollments",
        verbose_name="Прогресс",
    )

    class Meta:
        db_table = "enrollments"
        verbose_name = "Зачисление"
        verbose_name_plural = "Зачисления"
        unique_together = ("student", "course")
        ordering = ["-enrolled_at"]
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["course"]),
        ]

    def __str__(self):
        return f"{self.student.email} -> {self.course.title}"


class Progress(models.Model):
    """
    Модель прогресса студента по урокам в рамках зачисления.

    Отслеживает, какие уроки студент завершил в каждом курсе.
    """

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="lesson_progress",
        verbose_name="Зачисление",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="progress_records",
        verbose_name="Урок",
    )
    is_completed = models.BooleanField(default=False, verbose_name="Завершен")
    completed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата завершения"
    )

    class Meta:
        db_table = "progress"
        verbose_name = "Прогресс"
        verbose_name_plural = "Прогресс"
        unique_together = ("enrollment", "lesson")
        ordering = ["lesson__order"]
        indexes = [
            models.Index(fields=["enrollment"]),
            models.Index(fields=["lesson"]),
        ]

    def __str__(self):
        status = "✓" if self.is_completed else "✗"
        return f"{status} {self.enrollment.student.email} - {self.lesson.title}"
