from unittest.mock import patch

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

from cloud_sync_service.models import SyncJob
from cloud_sync_service.services import (
    enqueue_complaint_sync,
    enqueue_history_sync,
    enqueue_notification_sync,
    process_pending_sync_jobs,
)
from complaint_records.models import Complaint
from complaint_history.models import ComplaintHistory
from user_notifications.models import Notification


class SyncQueueTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="sync_test_user", password="test-password-123")
        self.complaint = Complaint.objects.create(
            created_by=self.user,
            title="Network is unavailable",
            description="The office network is not working.",
            category="Technical",
            priority="Medium",
        )

    def test_complaint_enqueue_is_idempotent_for_same_local_object(self):
        enqueue_complaint_sync(self.complaint)
        enqueue_complaint_sync(self.complaint)
        jobs = SyncJob.objects.filter(model_name="complaint", object_id=str(self.complaint.pk))
        self.assertEqual(jobs.count(), 1)
        self.assertEqual(jobs.first().payload["complaint_id"], self.complaint.complaint_id)

    def test_sync_without_uri_does_not_delete_queue(self):
        enqueue_complaint_sync(self.complaint)
        with override_settings(MONGODB_URI=""):
            result = process_pending_sync_jobs()
        self.assertEqual(result["processed"], 0)
        self.assertEqual(
            SyncJob.objects.filter(model_name="complaint", object_id=str(self.complaint.pk)).count(),
            1,
        )

    def test_history_enqueue(self):
        history = ComplaintHistory.objects.create(
            complaint=self.complaint,
            changed_by=self.user,
            old_status="",
            new_status=self.complaint.status,
            note="Initial test record",
        )
        enqueue_history_sync(history)
        self.assertTrue(SyncJob.objects.filter(model_name="history", object_id=str(history.pk)).exists())

    def test_notification_enqueue(self):
        notification = Notification.objects.create(
            user=self.user,
            title="Test",
            message="Test notification",
        )
        enqueue_notification_sync(notification)
        self.assertTrue(SyncJob.objects.filter(model_name="notification", object_id=str(notification.pk)).exists())


class MongoFailureRecoveryTests(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user(username="sync_fail_user", password="test-password-123")
        self.complaint = Complaint.objects.create(
            created_by=user,
            title="Cloud offline",
            description="Test retry queue",
            category="General",
            priority="Low",
        )
        enqueue_complaint_sync(self.complaint)

    @patch("cloud_sync_service.services._client", side_effect=RuntimeError("MongoDB unavailable in test"))
    @override_settings(MONGODB_URI="mongodb://mocked.invalid/test", CLOUD_SYNC_RETRY_SECONDS=1)
    def test_cloud_failure_marks_job_failed_and_keeps_it(self, mocked_client):
        result = process_pending_sync_jobs()
        self.assertEqual(result["failed"], 1)
        job = SyncJob.objects.get(model_name="complaint", object_id=str(self.complaint.pk))
        self.assertEqual(job.status, SyncJob.Status.FAILED)
        self.assertIn("MongoDB unavailable", job.last_error)
