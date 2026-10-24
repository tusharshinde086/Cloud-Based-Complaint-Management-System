from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

def health_check(request):
    return JsonResponse({"status": "ok", "application": "Cloud-Based Complaint Management System"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health_check"),
    path("accounts/", include("complaint_accounts.urls")),
    path("complaints/", include("complaint_records.urls")),
    path("", include("complaint_accounts.urls")),
    path("notifications/", include("user_notifications.urls")),
path("analytics/", include("analytics_dashboard.urls")),
path("reports/", include("pdf_reports.urls")),
path("ai/", include("complaint_classifier.urls")),
]
