import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone

def make_complaint_id():
    return f"CMP-{uuid.uuid4().hex[:10].upper()}"

class Complaint(models.Model):
    class Category(models.TextChoices):
        GENERAL = "general", "General"
        TECHNICAL = "technical", "Technical"
        FACILITIES = "facilities", "Facilities"
        BILLING = "billing", "Billing"
        SERVICE = "service", "Service"
        OTHER = "other", "Other"
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ASSIGNED = "assigned", "Assigned"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    complaint_id = models.CharField(max_length=20, unique=True, default=make_complaint_id, editable=False, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="submitted_complaints")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_complaints")
    title = models.CharField(max_length=180)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.GENERAL, db_index=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    attachment = models.FileField(upload_to="complaint_attachments/%Y/%m/", null=True, blank=True)
    resolution_note = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "category"]), models.Index(fields=["created_by", "created_at"]), models.Index(fields=["assigned_to", "status"])]

    def __str__(self):
        return f"{self.complaint_id} - {self.title}"

    def set_status(self, new_status, actor=None, remarks=""):
        if new_status not in self.Status.values:
            raise ValueError(f"Invalid complaint status: {new_status}")
        old_status = self.status
        if old_status == new_status:
            return
        self.status = new_status
        self.resolved_at = timezone.now() if new_status == self.Status.RESOLVED else None
        self.save(update_fields=["status", "resolved_at", "updated_at"])
        from complaint_history.models import ComplaintHistory
        ComplaintHistory.objects.create(complaint=self, actor=actor, old_status=old_status, new_status=new_status, remarks=remarks)
