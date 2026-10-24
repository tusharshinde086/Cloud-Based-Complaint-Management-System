import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.apps import apps


EXPECTED_APPS = [
    "complaint_accounts",
    "complaint_records",
    "complaint_history",
    "user_notifications",
    "pdf_reports",
    "analytics_dashboard",
    "complaint_classifier",
    "cloud_sync_service",
]


class Command(BaseCommand):
    help = "Run a local readiness review of Django configuration, MySQL, migrations, and optional cloud sync."

    def handle(self, *args, **options):
        errors = []
        warnings = []
        passed = []

        for app_name in EXPECTED_APPS:
            try:
                apps.get_app_config(app_name)
                passed.append(f"App installed: {app_name}")
            except LookupError:
                errors.append(f"Missing INSTALLED_APPS entry: {app_name}")

        try:
            connection.ensure_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            passed.append(f"Primary database reachable: {connection.vendor}")
        except Exception as exc:
            errors.append(f"Primary database connection failed: {exc}")

        try:
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            if plan:
                warnings.append(f"{len(plan)} migration operation(s) are unapplied. Run: python manage.py migrate")
            else:
                passed.append("Database migrations are up to date")
        except Exception as exc:
            errors.append(f"Could not inspect migrations: {exc}")

        secret_key = getattr(settings, "SECRET_KEY", "")
        if not secret_key or secret_key in ("change-me", "replace-with-a-long-random-secret", "django-insecure-change-me"):
            warnings.append("SECRET_KEY may be missing or a placeholder. Set a unique secret in .env.")
        else:
            passed.append("SECRET_KEY is configured")

        if getattr(settings, "DEBUG", True):
            warnings.append("DEBUG=True. Set DEBUG=False for production.")
        else:
            passed.append("DEBUG=False")

        allowed_hosts = getattr(settings, "ALLOWED_HOSTS", [])
        if not allowed_hosts:
            warnings.append("ALLOWED_HOSTS is empty.")
        elif "*" in allowed_hosts:
            warnings.append("ALLOWED_HOSTS contains '*'; restrict hosts in production.")
        else:
            passed.append("ALLOWED_HOSTS is configured")

        mongodb_uri = getattr(settings, "MONGODB_URI", os.getenv("MONGODB_URI", ""))
        if mongodb_uri:
            passed.append("MongoDB URI is configured (value not displayed)")
        else:
            warnings.append("MONGODB_URI is empty; cloud sync will not run.")

        self.stdout.write(self.style.SUCCESS("\nPASSED"))
        for item in passed:
            self.stdout.write(self.style.SUCCESS(f"  [OK] {item}"))

        self.stdout.write(self.style.WARNING("\nWARNINGS"))
        if warnings:
            for item in warnings:
                self.stdout.write(self.style.WARNING(f"  [WARN] {item}"))
        else:
            self.stdout.write("  None")

        if errors:
            self.stdout.write(self.style.ERROR("\nERRORS"))
            for item in errors:
                self.stdout.write(self.style.ERROR(f"  [ERROR] {item}"))
            raise SystemExit(1)

        self.stdout.write(self.style.SUCCESS("\nReadiness review completed. Review warnings before deployment."))
