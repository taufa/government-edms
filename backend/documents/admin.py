from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (
    DocumentAssignment,
    DocumentWorkflowLog,
    InwardDocument,
)

User = get_user_model()


class DocumentAssignmentInline(admin.TabularInline):
    model = DocumentAssignment
    extra = 0
    readonly_fields = ("assigned_at",)


class DocumentWorkflowLogInline(admin.TabularInline):
    model = DocumentWorkflowLog
    extra = 0
    readonly_fields = (
        "from_status",
        "to_status",
        "action_by",
        "comment",
        "created_at",
    )
    can_delete = False


@admin.register(InwardDocument)
class InwardDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "reference_number",
        "title",
        "sender",
        "received_date",
        "classification",
        "status",
        "assigned_hod",
    )

    list_filter = (
        "classification",
        "status",
        "received_date",
    )

    search_fields = (
        "reference_number",
        "title",
        "sender",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = [
        DocumentAssignmentInline,
        DocumentWorkflowLogInline,
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_hod":
            kwargs["queryset"] = User.objects.filter(
                roles__code__in=["HOD", "ACTING_HOD"],
                is_active=True,
            ).distinct()

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs,
        )


@admin.register(DocumentAssignment)
class DocumentAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "document",
        "assigned_by",
        "assigned_to",
        "assigned_at",
    )
    search_fields = (
        "document__reference_number",
        "document__title",
        "assigned_to__username",
    )


@admin.register(DocumentWorkflowLog)
class DocumentWorkflowLogAdmin(admin.ModelAdmin):
    list_display = (
        "document",
        "from_status",
        "to_status",
        "action_by",
        "created_at",
    )

    list_filter = (
        "from_status",
        "to_status",
        "created_at",
    )

    search_fields = (
        "document__reference_number",
        "document__title",
        "action_by__username",
    )