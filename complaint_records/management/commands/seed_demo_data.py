
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from complaint_records.models import Complaint
from complaint_history.models import ComplaintHistory
from user_notifications.models import Notification
from cloud_sync_service.integration import (
    queue_complaint_after_commit,
    queue_history_after_commit,
    queue_notification_after_commit,
)


DEMO_ITEMS = [
    ("Internet connection issue", "Internet access is unstable."),
    ("Water leakage", "Water is leaking near the building entrance."),
    ("Broken projector", "The projector does not turn on."),
    ("Streetlight not working", "The streetlight is not working."),
    ("Delayed service request", "The service request has been delayed."),
    ("Electrical maintenance", "An electrical socket needs inspection."),
    ("Cleanliness complaint", "The common area needs cleaning."),
    ("Network access request", "Network access needs restoration."),
    ("Parking management", "Vehicles block the designated parking area."),
    ("Equipment repair", "Office equipment requires repair."),
    ("Safety inspection", "A safety inspection is requested."),
    ("General facility issue", "Please inspect this facility issue."),
]


class Command(BaseCommand):
    help = "Create demonstration complaints, history, notifications and sync jobs."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default=None,
            help="Username to own the demo complaints.",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]

        if username:
            user = User.objects.filter(
                username=username,
                is_active=True,
            ).first()
        else:
            user = User.objects.filter(
                username__icontains="mohit",
                is_active=True,
            ).first()

            if user is None:
                user = User.objects.filter(
                    is_active=True,
                ).order_by("id").first()

        if user is None:
            raise CommandError(
                "No active user found. Register a user or pass --username."
            )

        categories = list(Complaint.Category.choices)
        priorities = list(Complaint.Priority.choices)
        statuses = list(Complaint.Status.choices)

        if not categories or not priorities or not statuses:
            raise CommandError(
                "The Complaint model needs category, priority and status choices."
            )

        created = 0
        skipped = 0

        with transaction.atomic():
            for index, (title, description) in enumerate(DEMO_ITEMS):
                demo_title = f"DEMO - {title}"

                if Complaint.objects.filter(
                    created_by=user,
                    title=demo_title,
                ).exists():
                    skipped += 1
                    continue

                status = statuses[index % len(statuses)][0]
                priority = priorities[index % len(priorities)][0]
                category = categories[index % len(categories)][0]

                complaint = Complaint.objects.create(
                    created_by=user,
                    title=demo_title,
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

                # These callbacks run after the transaction commits.
                queue_complaint_after_commit(complaint.pk)
                queue_history_after_commit(history.pk)
                queue_notification_after_commit(notification.pk)

                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Demo user: {user.username}"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"New complaints created: {created}"
        ))
        self.stdout.write(f"Existing demo complaints skipped: {skipped}")
        self.stdout.write(f"Total complaints: {Complaint.objects.count()}")
        self.stdout.write(
            f"Total history records: {ComplaintHistory.objects.count()}"
        )
        self.stdout.write(
            f"Total notifications: {Notification.objects.count()}"
        )
