from django.urls import path
from . import views

urlpatterns = [
    path("video-url/", views.VideoURLView.as_view(), name="video-url"),
]
