from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from complaint_accounts.models import UserProfile
from complaint_history.models import ComplaintHistory
from user_notifications.models import Notification
from .forms import ComplaintCreateForm, ComplaintUpdateForm
from .models import Complaint

def is_admin(user, profile=None):
    if user.is_superuser or user.is_staff:
        return True
    if profile is None:
        profile = UserProfile.objects.filter(user=user).first()
    return bool(profile and profile.role == UserProfile.Role.ADMIN)

def is_staff_role(user, profile=None):
    if user.is_superuser or user.is_staff:
        return True
    if profile is None:
        profile = UserProfile.objects.filter(user=user).first()
    return bool(profile and profile.role in {UserProfile.Role.STAFF, UserProfile.Role.ADMIN})

def visible_complaints(user):
    profile = UserProfile.objects.filter(user=user).first()
    if is_admin(user, profile):
        return Complaint.objects.all()
    if is_staff_role(user, profile):
        return Complaint.objects.filter(Q(assigned_to=user) | Q(created_by=user))
    return Complaint.objects.filter(created_by=user)

@login_required
def complaint_list(request):
    qs = visible_complaints(request.user).select_related("created_by", "assigned_to")
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    category = request.GET.get("category", "").strip()
    priority = request.GET.get("priority", "").strip()
    if query:
        qs = qs.filter(
            Q(complaint_id__icontains=query) | Q(title__icontains=query) |
            Q(description__icontains=query) | Q(created_by__username__icontains=query) |
            Q(assigned_to__username__icontains=query)
        )
    if status in Complaint.Status.values:
        qs = qs.filter(status=status)
    if category in Complaint.Category.values:
        qs = qs.filter(category=category)
    if priority in Complaint.Priority.values:
        qs = qs.filter(priority=priority)
    return render(request, "complaints/list.html", {
        "complaints": qs, "q": query, "selected_status": status,
        "selected_category": category, "selected_priority": priority,
        "statuses": Complaint.Status.choices, "categories": Complaint.Category.choices,
        "priorities": Complaint.Priority.choices,
    })

@login_required
@require_http_methods(["GET", "POST"])
def complaint_create(request):
    form = ComplaintCreateForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        complaint = form.save(commit=False)
        complaint.created_by = request.user
        complaint.save()
        ComplaintHistory.objects.create(
            complaint=complaint, actor=request.user, old_status="",
            new_status=complaint.status, remarks="Complaint submitted.",
        )
        Notification.objects.create(
            user=request.user, title="Complaint submitted",
            message=f"Your complaint {complaint.complaint_id} has been submitted.",
        )
        messages.success(request, f"Complaint submitted. Your ID is {complaint.complaint_id}.")
        return redirect("complaint_detail", pk=complaint.pk)
    return render(request, "complaints/form.html", {"form": form, "page_title": "Submit a complaint"})

@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint.objects.select_related("created_by", "assigned_to"), pk=pk)
    if not visible_complaints(request.user).filter(pk=complaint.pk).exists():
        raise PermissionDenied("You cannot view this complaint.")
    return render(request, "complaints/detail.html", {
        "complaint": complaint,
        "history": complaint.history.select_related("actor").all(),
        "can_manage": is_staff_role(request.user),
        "can_edit": complaint.created_by_id == request.user.id and complaint.status == Complaint.Status.PENDING,
    })

@login_required
@require_http_methods(["GET", "POST"])
def complaint_edit(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if complaint.created_by_id != request.user.id or complaint.status != Complaint.Status.PENDING:
        raise PermissionDenied("Only the complaint owner can edit a pending complaint.")
    form = ComplaintUpdateForm(request.POST or None, instance=complaint)
    if request.method == "POST" and form.is_valid():
        form.save()
        ComplaintHistory.objects.create(
            complaint=complaint, actor=request.user, old_status=complaint.status,
            new_status=complaint.status, remarks="Complaint details updated.",
        )
        messages.success(request, "Complaint updated.")
        return redirect("complaint_detail", pk=complaint.pk)
    return render(request, "complaints/form.html", {"form": form, "page_title": "Edit complaint"})

@login_required
@require_http_methods(["POST"])
def complaint_assign(request, pk):
    if not is_admin(request.user):
        raise PermissionDenied("Only administrators can assign complaints.")
    complaint = get_object_or_404(Complaint, pk=pk)
    staff_id = request.POST.get("assigned_to", "").strip()
    from django.contrib.auth import get_user_model
    User = get_user_model()
    staff_user = get_object_or_404(User, pk=staff_id, is_active=True)
    if not is_staff_role(staff_user):
        messages.error(request, "Choose a user whose profile role is Staff or Admin.")
        return redirect("complaint_detail", pk=complaint.pk)
    old_status = complaint.status
    complaint.assigned_to = staff_user
    if complaint.status == Complaint.Status.PENDING:
        complaint.status = Complaint.Status.ASSIGNED
    complaint.save(update_fields=["assigned_to", "status", "updated_at"])
    ComplaintHistory.objects.create(
        complaint=complaint, actor=request.user, old_status=old_status,
        new_status=complaint.status, remarks=f"Assigned to {staff_user.username}.",
    )
    Notification.objects.create(
        user=staff_user, title="Complaint assigned",
        message=f"Complaint {complaint.complaint_id} was assigned to you.",
    )
    Notification.objects.create(
        user=complaint.created_by, title="Complaint assignment updated",
        message=f"Complaint {complaint.complaint_id} has been assigned.",
    )
    messages.success(request, "Complaint assigned.")
    return redirect("complaint_detail", pk=complaint.pk)

@login_required
@require_http_methods(["POST"])
def complaint_change_status(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    profile = UserProfile.objects.filter(user=request.user).first()
    if not is_staff_role(request.user, profile):
        raise PermissionDenied("Only staff or administrators can update complaint status.")
    if not is_admin(request.user, profile) and complaint.assigned_to_id != request.user.id:
        raise PermissionDenied("You can only update complaints assigned to you.")
    new_status = request.POST.get("status", "")
    remarks = request.POST.get("remarks", "").strip()
    if new_status not in Complaint.Status.values:
        messages.error(request, "Invalid status selected.")
        return redirect("complaint_detail", pk=complaint.pk)
    old_status = complaint.status
    if old_status == new_status:
        messages.info(request, "Complaint already has that status.")
        return redirect("complaint_detail", pk=complaint.pk)
    complaint.status = new_status
    complaint.resolution_note = remarks if new_status in {Complaint.Status.RESOLVED, Complaint.Status.CLOSED} else complaint.resolution_note
    complaint.resolved_at = timezone.now() if new_status in {Complaint.Status.RESOLVED, Complaint.Status.CLOSED} else None
    complaint.save(update_fields=["status", "resolution_note", "resolved_at", "updated_at"])
    ComplaintHistory.objects.create(
        complaint=complaint, actor=request.user, old_status=old_status,
        new_status=new_status, remarks=remarks,
    )
    Notification.objects.create(
        user=complaint.created_by, title="Complaint status updated",
        message=f"Complaint {complaint.complaint_id} is now {complaint.get_status_display()}.",
    )
    messages.success(request, "Complaint status updated.")
    return redirect("complaint_detail", pk=complaint.pk)
