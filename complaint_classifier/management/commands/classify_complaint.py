from django.core.management.base import BaseCommand, CommandError
from complaint_classifier.services import classify_complaint


class Command(BaseCommand):
    help = "Classify a complaint from its title and description."

    def add_arguments(self, parser):
        parser.add_argument("--title", default="")
        parser.add_argument("--description", default="")

    def handle(self, *args, **options):
        if not options["title"].strip() and not options["description"].strip():
            raise CommandError("Provide --title and/or --description.")
        result = classify_complaint(options["title"], options["description"])
        self.stdout.write(self.style.SUCCESS(
            f"Category: {result['category']} | Method: {result['method']} | "
            f"Confidence: {result['confidence']}"
        ))
