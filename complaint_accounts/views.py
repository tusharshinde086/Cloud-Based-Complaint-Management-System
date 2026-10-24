from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from .forms import RegistrationForm
from .models import UserProfile

@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account has been created.")
        return redirect("dashboard")
    return render(request, "accounts/register.html", {"form": form})

@login_required
def dashboard_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    from complaint_records.models import Complaint
    if request.user.is_superuser or request.user.is_staff or profile.role == UserProfile.Role.ADMIN:
        qs = Complaint.objects.all()
    elif profile.role == UserProfile.Role.STAFF:
        qs = Complaint.objects.filter(assigned_to=request.user)
    else:
        qs = Complaint.objects.filter(created_by=request.user)
    return render(request, "accounts/dashboard.html", {
        "profile": profile, "total_complaints": qs.count(),
        "pending_complaints": qs.filter(status="pending").count(),
        "in_progress_complaints": qs.filter(status="in_progress").count(),
        "resolved_complaints": qs.filter(status__in=["resolved", "closed"]).count(),
        "recent_complaints": qs[:8],
    })
