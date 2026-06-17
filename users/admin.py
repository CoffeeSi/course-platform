from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, User, Verification


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    ordering = ("email",)
    list_display = ("email", "role", "is_active", "is_email_verified", "is_phone_verified")
    list_filter = ("role", "is_active", "is_email_verified", "is_phone_verified")
    search_fields = ("email", "phone_number")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("phone_number", "role")}),
        (
            "Verification",
            {"fields": ("is_email_verified", "is_phone_verified")},
        ),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role"),
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "verification_type", "is_used", "expires_at", "created_at")
    list_filter = ("verification_type", "is_used")
    search_fields = ("user__email", "code")
    readonly_fields = ("created_at",)
