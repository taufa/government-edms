from django.conf import settings
from django.db import models


class InwardDocument(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "RECEIVED", "Received"
        REGISTERED = "REGISTERED", "Registered"
        CHIEF_SECRETARY_REVIEW = (
            "CHIEF_SECRETARY_REVIEW",
            "Chief Secretary Review",
        )
        ASSIGNED_TO_HOD = "ASSIGNED_TO_HOD", "Assigned to HOD"
        OFFICER_ACTION = "OFFICER_ACTION", "Officer Action"
        HOD_REVIEW = "HOD_REVIEW", "HOD Review"
        CHIEF_SECRETARY_FINAL_REVIEW = (
            "CHIEF_SECRETARY_FINAL_REVIEW",
            "Chief Secretary Final Review",
        )
        COMPLETED = "COMPLETED", "Completed"
        ARCHIVED = "ARCHIVED", "Archived"

    class Classification(models.TextChoices):
        PUBLIC = "PUBLIC", "Public"
        INTERNAL = "INTERNAL", "Internal"
        CONFIDENTIAL = "CONFIDENTIAL", "Confidential"
        SECRET = "SECRET", "Secret"

    title = models.CharField(max_length=255)
    reference_number = models.CharField(max_length=100, unique=True)

    sender = models.CharField(max_length=255, blank=True)
    received_date = models.DateField()

    classification = models.CharField(
        max_length=50,
        choices=Classification.choices,
        default=Classification.INTERNAL,
    )

    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.RECEIVED,
    )

    assigned_hod = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="hod_documents",
        on_delete=models.SET_NULL,
    )

    assigned_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="officer_documents",
        on_delete=models.SET_NULL,
    )

    paperless_document_id = models.PositiveIntegerField(null=True, blank=True)
    paperless_document_url = models.URLField(blank=True)

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="created_inward_documents",
        on_delete=models.SET_NULL,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-received_date", "-created_at"]

    def __str__(self):
        return f"{self.reference_number} - {self.title}"
    
    def can_transition_to(self, new_status):
        allowed_transitions = {
            self.Status.RECEIVED: [
                self.Status.REGISTERED,
            ],
            self.Status.REGISTERED: [
                self.Status.CHIEF_SECRETARY_REVIEW,
            ],
            self.Status.CHIEF_SECRETARY_REVIEW: [
                self.Status.ASSIGNED_TO_HOD,
            ],
            self.Status.ASSIGNED_TO_HOD: [
                self.Status.HOD_REVIEW,
            ],
            self.Status.HOD_REVIEW: [
                self.Status.CHIEF_SECRETARY_FINAL_REVIEW,
            ],
            self.Status.CHIEF_SECRETARY_FINAL_REVIEW: [
                self.Status.COMPLETED,
                self.Status.ARCHIVED,
            ],
            self.Status.COMPLETED: [
                self.Status.ARCHIVED,
            ],
        }

        return new_status in allowed_transitions.get(self.status, [])

    def transition_to(self, new_status, user=None, comment=""):
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Cannot transition from {self.status} to {new_status}"
            )

        old_status = self.status
        self.status = new_status
        self.save(update_fields=["status", "updated_at"])

        DocumentWorkflowLog.objects.create(
            document=self,
            from_status=old_status,
            to_status=new_status,
            action_by=user,
            comment=comment,
        )
    
class DocumentAssignment(models.Model):
    document = models.ForeignKey(
        InwardDocument,
        related_name="assignments",
        on_delete=models.CASCADE,
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="document_assignments_made",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="document_assignments_received",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    note = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-assigned_at"]

    def __str__(self):
        return f"{self.document.reference_number} assigned to {self.assigned_to}"


class DocumentWorkflowLog(models.Model):
    document = models.ForeignKey(
        InwardDocument,
        related_name="workflow_logs",
        on_delete=models.CASCADE,
    )

    from_status = models.CharField(
        max_length=50,
        choices=InwardDocument.Status.choices,
        blank=True,
    )

    to_status = models.CharField(
        max_length=50,
        choices=InwardDocument.Status.choices,
    )

    action_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="document_workflow_actions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.document.reference_number}: {self.from_status} → {self.to_status}"