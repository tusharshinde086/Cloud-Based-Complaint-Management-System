from django.core.management.base import BaseCommand
from cloud_sync_service.services import process_pending_sync_jobs


class Command(BaseCommand):
    help = "Synchronize queued complaint-system records from MySQL to MongoDB Atlas."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=None)

    def handle(self, *args, **options):
        result = process_pending_sync_jobs(limit=options["limit"])
        self.stdout.write(
            f"Processed: {result['processed']} | Synced: {result['synced']} | "
            f"Failed: {result['failed']} | {result['message']}"
        )
