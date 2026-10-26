
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from pymongo import MongoClient
from pymongo.errors import PyMongoError


class Command(BaseCommand):
    help = "Check the MongoDB Atlas connection."

    def handle(self, *args, **options):
        uri = getattr(settings, "MONGODB_URI", "")
        database_name = getattr(
            settings,
            "MONGODB_DATABASE",
            "complaint_management_cloud",
        )

        if not uri:
            raise CommandError(
                "MONGODB_URI is empty. Configure it in .env."
            )

        client = None

        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=10000)
            client.admin.command("ping")

            database = client[database_name]
            self.stdout.write(
                self.style.SUCCESS(
                    "MongoDB connection successful."
                )
            )
            self.stdout.write(f"Database configured: {database.name}")

        except PyMongoError as exc:
            raise CommandError(
                f"MongoDB connection failed: {exc}"
            ) from exc

        finally:
            if client is not None:
                client.close()
