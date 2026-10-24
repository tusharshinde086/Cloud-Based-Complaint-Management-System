from django.db import transaction

from .services import (
    enqueue_complaint_sync,
    enqueue_history_sync,
    enqueue_notification_sync,
)


def queue_complaint_after_commit(complaint_id):
    """Queue the latest persisted complaint state after its transaction commits."""
    def _enqueue():
        from complaint_records.models import Complaint
        try:
            complaint = Complaint.objects.select_related("created_by", "assigned_to").get(pk=complaint_id)
            enqueue_complaint_sync(complaint)
        except Complaint.DoesNotExist:
            return
    transaction.on_commit(_enqueue)


def queue_history_after_commit(history_id):
    def _enqueue():
        from complaint_history.models import ComplaintHistory
        try:
            history = ComplaintHistory.objects.select_related(
                "complaint", "changed_by"
            ).get(pk=history_id)
            enqueue_history_sync(history)
        except ComplaintHistory.DoesNotExist:
            return
    transaction.on_commit(_enqueue)


def queue_notification_after_commit(notification_id):
    def _enqueue():
        from user_notifications.models import Notification
        try:
            notification = Notification.objects.select_related("user").get(pk=notification_id)
            enqueue_notification_sync(notification)
        except Notification.DoesNotExist:
            return
    transaction.on_commit(_enqueue)
