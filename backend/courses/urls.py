from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CourseViewSet, ModuleViewSet, LessonViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('modules', ModuleViewSet, basename='module')
router.register('lessons', LessonViewSet, basename='lesson')
router.register('', CourseViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls)),
]
