from django.core.management.base import BaseCommand
from cloud_sync_service.models import SyncJob


class Command(BaseCommand):
    help = "Show the local MySQL queue status for MongoDB synchronization."

    def handle(self, *args, **options):
        for status, label in SyncJob.Status.choices:
            count = SyncJob.objects.filter(status=status).count()
            self.stdout.write(f"{label}: {count}")
        self.stdout.write(f"Total: {SyncJob.objects.count()}")
