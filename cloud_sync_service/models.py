from django.db import models
class SyncJob(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SYNCED = "synced", "Synced"
        FAILED = "failed", "Failed"
    model_label = models.CharField(max_length=120)
    object_id = models.CharField(max_length=100)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING, db_index=True)
    attempts = models.PositiveIntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["created_at"]
        constraints = [models.UniqueConstraint(fields=["model_label", "object_id"], name="unique_cloud_sync_object")]
    def __str__(self):
        return f"{self.model_label}:{self.object_id} ({self.status})"
