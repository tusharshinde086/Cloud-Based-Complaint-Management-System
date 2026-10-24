from django.contrib import admin
from .models import ComplaintHistory
@admin.register(ComplaintHistory)
class ComplaintHistoryAdmin(admin.ModelAdmin):
    list_display = ("complaint", "old_status", "new_status", "actor", "created_at")
    list_filter = ("old_status", "new_status", "created_at")
    search_fields = ("complaint__complaint_id", "complaint__title", "remarks", "actor__username")
