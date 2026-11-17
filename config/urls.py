
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import RedirectView


def health_check(request):
    return JsonResponse({
        "status": "ok",
        "application": "Cloud-Based Complaint Management System",
    })


urlpatterns = [
    # Homepage redirects to login.
    path(
        "",
        RedirectView.as_view(
            pattern_name="login",
            permanent=False,
        ),
        name="home",
    ),

    path("admin/", admin.site.urls),
    path("health/", health_check, name="health_check"),

    # Authentication, registration, dashboard and logout.
    path("", include("complaint_accounts.urls")),

    # Complaint management.
    path("complaints/", include("complaint_records.urls")),
    

    # Other modules.
    path("notifications/", include("user_notifications.urls")),
    path("analytics/", include("analytics_dashboard.urls")),
    path("reports/", include("pdf_reports.urls")),
    path("ai/", include("complaint_classifier.urls")),
]
