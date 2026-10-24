from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from complaint_records.models import Complaint


class ComplaintWorkflowSmokeTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="complaint_test_user", password="test-password-123")
        self.complaint = Complaint.objects.create(
            created_by=self.user,
            title="Test complaint",
            description="This is a test complaint.",
            category="General",
            priority="Medium",
        )

    def test_complaint_list_requires_login(self):
        response = self.client.get(reverse("complaint_list"))
        self.assertEqual(response.status_code, 302)

    def test_owner_can_view_own_complaint(self):
        self.client.login(username="complaint_test_user", password="test-password-123")
        response = self.client.get(reverse("complaint_detail", args=[self.complaint.pk]))
        self.assertEqual(response.status_code, 200)
