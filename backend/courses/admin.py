from django.contrib import admin
from .models import Category, Course, Module, Lesson


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ("title", "order")


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ("title", "is_free", "order")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "instructor",
        "category",
        "price",
        "is_published",
        "created_at",
    )
    list_filter = ("is_published", "category", "created_at")
    search_fields = (
        "title",
        "instructor__first_name",
        "instructor__last_name",
        "instructor__email",
    )
    list_editable = ("is_published", "price")
    raw_id_fields = ("instructor",)
    inlines = [ModuleInline]
    date_hierarchy = "created_at"


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title", "course__title")
    list_editable = ("order",)
    inlines = [LessonInline]
    raw_id_fields = ("course",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "get_course", "module", "is_free", "order", "created_at")
    list_filter = ("is_free", "module__course", "module")
    search_fields = ("title", "module__title")
    list_editable = ("is_free", "order")
    raw_id_fields = ("module",)

    def get_course(self, obj):
        return obj.module.course.title

    def reorder_lessons(self, module):
        lessons = Lesson.objects.filter(module=module).order_by("order")
        for index, lesson in enumerate(lessons, start=1):
            if lesson.order != index:
                lesson.order = index
                lesson.save(update_fields=["order"])
