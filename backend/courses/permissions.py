from rest_framework import permissions
from courses.models import Lesson
from enrollments.models import Enrollment
from users.models import User


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает только чтение для обычных пользователей.
    Полный доступ (создание, изменение, удаление) только у администратора.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.role == User.Role.ADMIN or request.user.is_staff
        )


class IsCourseInstructorOrReadOnly(permissions.BasePermission):
    """
    Для курсов: только преподаватель этого курса или администратор может изменять его.
    Создавать курс могут только пользователи с ролью INSTRUCTOR или ADMIN.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.role in [User.Role.INSTRUCTOR, User.Role.ADMIN]
            or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            obj.instructor == request.user
            or request.user.role == User.Role.ADMIN
            or request.user.is_staff
        )


class IsModuleInstructorOrReadOnly(permissions.BasePermission):
    """
    Для модулей: только преподаватель курса, к которому принадлежит модуль, или админ.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.role in [User.Role.INSTRUCTOR, User.Role.ADMIN]
            or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            obj.course.instructor == request.user
            or request.user.role == User.Role.ADMIN
            or request.user.is_staff
        )


class IsLessonInstructorOrReadOnly(permissions.BasePermission):
    """
    Для уроков: только преподаватель курса, к которому принадлежит урок, или админ.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.role in [User.Role.INSTRUCTOR, User.Role.ADMIN]
            or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            obj.module.course.instructor == request.user
            or request.user.role == User.Role.ADMIN
            or request.user.is_staff
        )


class IsEnrolledInCourseOrAdmin(permissions.BasePermission):
    """
    Доступ к конкретному уроку: только для админов, стаффа,
    или студентов, у которых есть активное зачисление на курс этого урока.
    """

    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated):
            return False

        user_role = getattr(request.user, "role", None)
        return (
            user_role in [User.Role.STUDENT, User.Role.ADMIN] or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        user_role = getattr(request.user, "role", None)

        if user_role == User.Role.ADMIN or request.user.is_staff:
            return True

        if user_role == User.Role.STUDENT:
            return Enrollment.objects.filter(
                student_id=request.user.id, course_id=obj.module.course_id
            ).exists()

        return False
