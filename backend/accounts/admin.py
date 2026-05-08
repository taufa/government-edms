from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Department, Position, Role, User


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    search_fields = ("name", "code")
    list_filter = ("is_active",)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    search_fields = ("name", "code")
    list_filter = ("is_active",)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Government EDMS Profile",
            {
                "fields": (
                    "job_title",
                    "department",
                    "position",
                    "roles",
                    "phone_number",
                )
            },
        ),
    )

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "job_title",
        "department",
        "position",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "job_title",
    )

    list_filter = (
        "department",
        "position",
        "roles",
        "is_staff",
        "is_active",
    )

    filter_horizontal = ("groups", "user_permissions", "roles")