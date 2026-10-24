from django.contrib import admin
from .models import SyncJob
@admin.register(SyncJob)
class SyncJobAdmin(admin.ModelAdmin):
    list_display = ("model_label", "object_id", "status", "attempts", "next_retry_at", "updated_at")
    list_filter = ("status", "model_label")
    search_fields = ("model_label", "object_id", "last_error")
