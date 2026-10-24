from django.conf import settings
from django.db import models

class ComplaintHistory(models.Model):
    complaint = models.ForeignKey("complaint_records.Complaint", on_delete=models.CASCADE, related_name="history")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="complaint_actions")
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"{self.complaint.complaint_id}: {self.old_status} -> {self.new_status}"
