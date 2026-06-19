from django.contrib import admin
from .models import Enrollment, Progress


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "course", "enrolled_at")
    list_filter = ("enrolled_at", "course")
    search_fields = ("student__email", "course__title")
    readonly_fields = ("enrolled_at",)
    ordering = ("-enrolled_at",)


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "lesson", "is_completed", "completed_at")
    list_filter = ("is_completed", "completed_at", "enrollment__course")
    search_fields = ("enrollment__student__email", "lesson__title")
    readonly_fields = ("completed_at",)
    ordering = ("enrollment", "lesson__order")
