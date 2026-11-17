
import logging

from django.db import transaction

logger = logging.getLogger(__name__)


def queue_complaint_after_commit(complaint_id):
    """
    Queue a complaint for MongoDB synchronization after the
    current database transaction commits successfully.
    """

    def _enqueue():
        from complaint_records.models import Complaint
        from .services import enqueue_complaint_sync

        try:
            complaint = (
                Complaint.objects
                .select_related("created_by", "assigned_to")
                .get(pk=complaint_id)
            )
            enqueue_complaint_sync(complaint)

        except Complaint.DoesNotExist:
            logger.warning(
                "Complaint %s no longer exists; sync job not queued.",
                complaint_id,
            )

        except Exception:
            # Keep the main complaint operation separate from cloud sync.
            logger.exception(
                "Could not enqueue complaint %s for cloud sync.",
                complaint_id,
            )

    transaction.on_commit(_enqueue)


def queue_history_after_commit(history_id):
    """
    Queue a complaint history record after its transaction commits.
    """

    def _enqueue():
        from complaint_history.models import ComplaintHistory
        from .services import enqueue_history_sync

        try:
            history = (
                ComplaintHistory.objects
                .select_related("complaint", "actor")
                .get(pk=history_id)
            )
            enqueue_history_sync(history)

        except ComplaintHistory.DoesNotExist:
            logger.warning(
                "Complaint history %s no longer exists; "
                "sync job not queued.",
                history_id,
            )

        except Exception:
            logger.exception(
                "Could not enqueue complaint history %s for cloud sync.",
                history_id,
            )

    transaction.on_commit(_enqueue)


def queue_notification_after_commit(notification_id):
    """
    Queue a notification after its transaction commits.
    """

    def _enqueue():
        from user_notifications.models import Notification
        from .services import enqueue_notification_sync

        try:
            notification = (
                Notification.objects
                .select_related("user")
                .get(pk=notification_id)
            )
            enqueue_notification_sync(notification)

        except Notification.DoesNotExist:
            logger.warning(
                "Notification %s no longer exists; "
                "sync job not queued.",
                notification_id,
            )

        except Exception:
            logger.exception(
                "Could not enqueue notification %s for cloud sync.",
                notification_id,
            )

    transaction.on_commit(_enqueue)
