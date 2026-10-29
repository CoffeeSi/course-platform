# users/permissions.py
from rest_framework import permissions


class IsEmailVerified(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_email_verified
