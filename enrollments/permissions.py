from rest_framework import permissions
from .models import Enrollment


class IsEnrolled(permissions.BasePermission):
    """
    Пермиссия проверяет, что пользователь зачислен на курс.
    Используется для защиты доступа к контенту курсов.
    """

    def has_permission(self, request, view):
        """Проверяет, может ли пользователь просматривать курс."""
        if request.method == "POST":
            return request.user and request.user.is_authenticated

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Проверяет доступ к конкретному уроку/модулю курса."""
        # obj должна быть Course или Lesson
        if hasattr(obj, "module"):
            # Это урок (Lesson)
            course = obj.module.course
        elif hasattr(obj, "modules"):
            # Это курс (Course)
            course = obj
        else:
            return False

        # Проверяем, зачислен ли пользователь на этот курс
        return Enrollment.objects.filter(student=request.user, course=course).exists()


class IsEnrollmentOwner(permissions.BasePermission):
    """
    Пермиссия проверяет, что пользователь может управлять только своим зачислением.
    """

    def has_object_permission(self, request, view, obj):
        """
        obj должна быть объектом Enrollment.
        Пользователь может управлять только своим зачислением.
        """
        return obj.student == request.user
