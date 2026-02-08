"""Management command to list all domains in VoidMail."""

from django.core.management.base import BaseCommand

from inbox.models import Domain


class Command(BaseCommand):
    help = "List all domains in VoidMail"

    def handle(self, *args, **options):
        domains = Domain.objects.all().order_by("name")

        if not domains:
            self.stdout.write("No domains configured.")
            self.stdout.write(f"Add one with: python manage.py adddomain <domain>")
            return

        self.stdout.write(f"{'Domain':<40} {'Status':<10} {'Created'}")
        self.stdout.write("-" * 70)

        for domain in domains:
            status = "active" if domain.is_active else "inactive"
            self.stdout.write(
                f"{domain.name:<40} {status:<10} {domain.created_at.strftime('%Y-%m-%d')}"
            )

        self.stdout.write("")
        self.stdout.write(f"Total: {domains.count()} domain(s)")
