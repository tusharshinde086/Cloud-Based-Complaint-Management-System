from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render

from complaint_records.models import Complaint
from complaint_accounts.models import UserProfile


def _role(user):
    if user.is_superuser or user.is_staff:
        return "Admin"
    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        return "User"


def _visible_complaints(user):
    role = _role(user)
    qs = Complaint.objects.all()
    if role == "Admin":
        return qs
    if role == "Staff":
        return qs.filter(assigned_to=user)
    return qs.filter(created_by=user)


@login_required
def analytics_page(request):
    complaints = _visible_complaints(request.user)
    statuses = list(
        complaints.values("status").annotate(total=Count("id")).order_by("status")
    )
    categories = list(
        complaints.values("category").annotate(total=Count("id")).order_by("category")
    )
    return render(request, "analytics_dashboard/analytics.html", {
        "status_data": statuses,
        "category_data": categories,
        "total_complaints": complaints.count(),
    })


@login_required
def analytics_data(request):
    complaints = _visible_complaints(request.user)
    statuses = list(
        complaints.values("status").annotate(total=Count("id")).order_by("status")
    )
    categories = list(
        complaints.values("category").annotate(total=Count("id")).order_by("category")
    )
    return JsonResponse({
        "total": complaints.count(),
        "statuses": statuses,
        "categories": categories,
    })
