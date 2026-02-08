"""Management command to add a domain to VoidMail."""

from django.core.management.base import BaseCommand, CommandError

from inbox.models import Domain


class Command(BaseCommand):
    help = "Add a domain to VoidMail"

    def add_arguments(self, parser):
        parser.add_argument(
            "domain",
            type=str,
            help="Domain name (e.g., mail.example.com)",
        )
        parser.add_argument(
            "--inactive",
            action="store_true",
            help="Create the domain as inactive",
        )

    def handle(self, *args, **options):
        domain_name = options["domain"].lower().strip()

        # Basic validation
        if "@" in domain_name:
            raise CommandError("Domain should not contain '@'")
        if "/" in domain_name:
            raise CommandError("Domain should not contain '/'")

        domain, created = Domain.objects.get_or_create(
            name=domain_name,
            defaults={"is_active": not options["inactive"]},
        )

        if created:
            status = "active" if domain.is_active else "inactive"
            self.stdout.write(
                self.style.SUCCESS(f"Created domain '{domain_name}' ({status})")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Domain '{domain_name}' already exists")
            )
