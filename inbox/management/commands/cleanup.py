"""Continuous cleanup of expired mailboxes."""

import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from inbox.models import Mailbox


class Command(BaseCommand):
    help = "Continuously delete expired mailboxes and their emails"

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval", type=int, default=60,
            help="Seconds between cleanup runs (default: 60)",
        )
        parser.add_argument(
            "--once", action="store_true",
            help="Run cleanup once and exit",
        )

    def handle(self, *args, **options):
        interval = options["interval"]
        once = options["once"]

        self.stdout.write(f"Cleanup service started (interval: {interval}s)")

        while True:
            count, _ = Mailbox.objects.filter(expires_at__lte=timezone.now()).delete()
            if count:
                self.stdout.write(f"Deleted {count} expired object(s)")

            if once:
                break

            time.sleep(interval)
