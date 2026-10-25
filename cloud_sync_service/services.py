
import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from .models import SyncJob

logger = logging.getLogger(__name__)

COLLECTIONS = {
    "complaint": "complaints",
    "history": "complaint_history",
    "notification": "notifications",
}


def _mongo_configured():
    return bool(getattr(settings, "MONGODB_URI", "").strip())


def _client():
    uri = getattr(settings, "MONGODB_URI", "")
    if not uri:
        raise RuntimeError("MONGODB_URI is not configured.")

    return MongoClient(
        uri,
        serverSelectionTimeoutMS=7000,
        connectTimeoutMS=7000,
    )


def _enqueue(model_label, object_id, payload):
    SyncJob.objects.update_or_create(
        model_label=model_label,
        object_id=str(object_id),
        defaults={
            "payload": payload,
            "status": SyncJob.Status.PENDING,
            "attempts": 0,
            "next_retry_at": timezone.now(),
            "last_error": "",
        },
    )


def _payload_for_complaint(complaint):
    return {
        "source": "cloud_based_complaint_management_system",
        "record_type": "complaint",
        "complaint_id": str(complaint.complaint_id),
        "title": complaint.title,
        "description": complaint.description,
        "category": complaint.category,
        "priority": complaint.priority,
        "status": complaint.status,
        "created_by_username": (
            complaint.created_by.get_username()
            if complaint.created_by else None
        ),
        "assigned_to_username": (
            complaint.assigned_to.get_username()
            if complaint.assigned_to else None
        ),
        "resolution_note": getattr(complaint, "resolution_note", ""),
        "created_at": (
            complaint.created_at.isoformat()
            if complaint.created_at else None
        ),
        "updated_at": (
            complaint.updated_at.isoformat()
            if complaint.updated_at else None
        ),
    }


def enqueue_complaint_sync(complaint):
    _enqueue(
        "complaint",
        complaint.pk,
        _payload_for_complaint(complaint),
    )


def enqueue_history_sync(history):
    actor = getattr(history, "actor", None)
    remarks = getattr(history, "remarks", "")

    payload = {
        "source": "cloud_based_complaint_management_system",
        "record_type": "history",
        "local_history_id": str(history.pk),
        "complaint_id": str(history.complaint.complaint_id),
        "actor_username": (
            actor.get_username() if actor else None
        ),
        "old_status": history.old_status,
        "new_status": history.new_status,
        "remarks": remarks,
        "created_at": (
            history.created_at.isoformat()
            if history.created_at else None
        ),
    }

    _enqueue("history", history.pk, payload)


def enqueue_notification_sync(notification):
    payload = {
        "source": "cloud_based_complaint_management_system",
        "record_type": "notification",
        "local_notification_id": str(notification.pk),
        "username": (
            notification.user.get_username()
            if notification.user else None
        ),
        "title": getattr(notification, "title", "Notification"),
        "message": notification.message,
        "is_read": getattr(notification, "is_read", False),
        "created_at": (
            notification.created_at.isoformat()
            if notification.created_at else None
        ),
    }

    _enqueue("notification", notification.pk, payload)


def process_pending_sync_jobs(limit=None):
    if not _mongo_configured():
        return {
            "processed": 0,
            "synced": 0,
            "failed": 0,
            "message": "MONGODB_URI is not configured.",
        }

    batch_size = limit or int(
        getattr(settings, "CLOUD_SYNC_BATCH_SIZE", 100)
    )
    retry_seconds = int(
        getattr(settings, "CLOUD_SYNC_RETRY_SECONDS", 60)
    )

    jobs = list(
        SyncJob.objects.filter(
            status__in=[
                SyncJob.Status.PENDING,
                SyncJob.Status.FAILED,
            ],
            next_retry_at__lte=timezone.now(),
        ).order_by("created_at")[:batch_size]
    )

    if not jobs:
        return {
            "processed": 0,
            "synced": 0,
            "failed": 0,
            "message": "No due sync jobs.",
        }

    synced = 0
    failed = 0
    client = None

    try:
        client = _client()
        client.admin.command("ping")

        database = client[
            getattr(
                settings,
                "MONGODB_DATABASE",
                "complaint_management_cloud",
            )
        ]

        for job in jobs:
            job.status = SyncJob.Status.PROCESSING
            job.save(update_fields=["status", "updated_at"])

            try:
                collection_name = COLLECTIONS.get(job.model_label)

                if not collection_name:
                    raise ValueError(
                        f"Unsupported sync model label: {job.model_label}"
                    )

                document = dict(job.payload)
                document["local_object_id"] = str(job.object_id)

                database[collection_name].replace_one(
                    {"local_object_id": str(job.object_id)},
                    document,
                    upsert=True,
                )

                job.status = SyncJob.Status.SYNCED
                job.last_error = ""
                job.save(
                    update_fields=[
                        "status",
                        "last_error",
                        "updated_at",
                    ]
                )
                synced += 1

            except (PyMongoError, ValueError, TypeError) as exc:
                failed += 1
                job.attempts += 1
                job.status = SyncJob.Status.FAILED
                job.last_error = str(exc)[:2000]

                delay = retry_seconds * min(
                    2 ** job.attempts, 60
                )
                job.next_retry_at = (
                    timezone.now() + timedelta(seconds=delay)
                )

                job.save(
                    update_fields=[
                        "attempts",
                        "status",
                        "last_error",
                        "next_retry_at",
                        "updated_at",
                    ]
                )

    except (PyMongoError, RuntimeError) as exc:
        failed = len(jobs)

        for job in jobs:
            job.attempts += 1
            job.status = SyncJob.Status.FAILED
            job.last_error = str(exc)[:2000]

            delay = retry_seconds * min(
                2 ** job.attempts, 60
            )
            job.next_retry_at = (
                timezone.now() + timedelta(seconds=delay)
            )

            job.save(
                update_fields=[
                    "attempts",
                    "status",
                    "last_error",
                    "next_retry_at",
                    "updated_at",
                ]
            )

        logger.warning(
            "MongoDB sync unavailable; jobs retained for retry: %s",
            exc,
        )

    finally:
        if client is not None:
            client.close()

    return {
        "processed": len(jobs),
        "synced": synced,
        "failed": failed,
        "message": "Sync attempt completed; failed jobs remain queued.",
    }
