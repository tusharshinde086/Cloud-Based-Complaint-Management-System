from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("complaint_id", "title", "category", "priority", "status", "created_by", "assigned_to", "created_at")
    list_filter = ("status", "category", "priority", "created_at")
    search_fields = ("complaint_id", "title", "description", "created_by__username", "assigned_to__username")
    readonly_fields = ("complaint_id", "created_at", "updated_at", "resolved_at")
