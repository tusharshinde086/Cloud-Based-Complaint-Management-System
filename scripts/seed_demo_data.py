
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from complaint_records.models import Complaint
from complaint_history.models import ComplaintHistory
from user_notifications.models import Notification
from cloud_sync_service.integration import (
    queue_complaint_after_commit,
    queue_history_after_commit,
    queue_notification_after_commit,
)

User = get_user_model()

# Find the intended demo user, or fall back to an active user.
user = User.objects.filter(
    username__icontains="mohit",
    is_active=True,
).first()

if user is None:
    user = User.objects.filter(is_active=True).first()

if user is None:
    raise SystemExit(
        "No active user found. Create an account first."
    )

categories = list(Complaint.Category.choices)
priorities = list(Complaint.Priority.choices)
statuses = list(Complaint.Status.choices)

if not categories or not priorities or not statuses:
    raise SystemExit(
        "Complaint model must define category, priority and status choices."
    )

demo_items = [
    ("Internet connection issue", "Internet access is unstable."),
    ("Water leakage", "Water is leaking near the entrance."),
    ("Broken projector", "The projector does not turn on."),
    ("Streetlight not working", "The streetlight is not working."),
    ("Delayed service request", "The service request is delayed."),
    ("Electrical maintenance", "An electrical socket needs inspection."),
    ("Cleanliness complaint", "The common area needs cleaning."),
    ("Network access request", "Network access needs restoration."),
    ("Parking management", "Vehicles block the designated area."),
    ("Equipment repair", "Office equipment requires repair."),
    ("Safety inspection", "A safety inspection is requested."),
    ("General facility issue", "Please inspect this facility issue."),
]

created_count = 0

with transaction.atomic():
    for i, (title, description) in enumerate(demo_items):
        # Avoid creating duplicates if the script is run again.
        if Complaint.objects.filter(
            created_by=user,
            title=f"DEMO - {title}",
        ).exists():
            continue

        status = statuses[i % len(statuses)][0]
        priority = priorities[i % len(priorities)][0]
        category = categories[i % len(categories)][0]

        complaint = Complaint.objects.create(
            created_by=user,
            title=f"DEMO - {title}",
            description=description,
            category=category,
            priority=priority,
            status=status,
        )

        if status in ("resolved", "closed"):
            complaint.resolved_at = (
                timezone.now() - timedelta(days=1)
            )
            complaint.save(update_fields=["resolved_at"])

        history = ComplaintHistory.objects.create(
            complaint=complaint,
            actor=user,
            old_status="",
            new_status=complaint.status,
            remarks="Demo data created for project testing.",
        )

        notification = Notification.objects.create(
            user=user,
            title="Demo complaint created",
            message=(
                f"Demo complaint {complaint.complaint_id} was created."
            ),
        )

        # Queue only after the transaction successfully commits.
        transaction.on_commit(
            lambda complaint_id=complaint.pk:
                queue_complaint_after_commit(complaint_id)
        )
        transaction.on_commit(
            lambda history_id=history.pk:
                queue_history_after_commit(history_id)
        )
        transaction.on_commit(
            lambda notification_id=notification.pk:
                queue_notification_after_commit(notification_id)
        )

        created_count += 1

print(f"Demo user: {user.username}")
print(f"New demo complaints: {created_count}")
print(f"Total complaints: {Complaint.objects.count()}")
print(f"Total history records: {ComplaintHistory.objects.count()}")
print(f"Total notifications: {Notification.objects.count()}")
