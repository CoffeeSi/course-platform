from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EnrollmentListCreateView,
    EnrollmentDetailView,
    ProgressViewSet,
    CheckCourseStatusView,
)

router = DefaultRouter()
router.register(r"progress", ProgressViewSet, basename="progress")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "enrollments/",
        EnrollmentListCreateView.as_view(),
        name="enrollment-list-create",
    ),
    path(
        "enrollments/<int:id>/",
        EnrollmentDetailView.as_view(),
        name="enrollment-detail",
    ),
    path(
        "enrollments/<int:course_id>/status/",
        CheckCourseStatusView.as_view(),
        name="check-course-status",
    ),
]
