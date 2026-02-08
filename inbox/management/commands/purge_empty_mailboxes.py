"""Purge mailboxes that are empty and older than 1 hour."""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone

from inbox.models import Mailbox


class Command(BaseCommand):
    help = "Delete mailboxes that are empty and older than 1 hour"

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours", type=int, default=1,
            help="Minimum age in hours before an empty mailbox can be deleted (default: 1)",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Show what would be deleted without actually deleting",
        )

    def handle(self, *args, **options):
        hours = options["hours"]
        dry_run = options["dry_run"]
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        # Find mailboxes older than cutoff with no non-deleted emails
        empty_mailboxes = Mailbox.objects.annotate(
            active_email_count=Count("emails", filter=Q(emails__is_deleted=False))
        ).filter(
            created_at__lte=cutoff_time,
            active_email_count=0
        )
        
        count = empty_mailboxes.count()
        
        if count == 0:
            self.stdout.write("No empty mailboxes to purge.")
            return
        
        if dry_run:
            self.stdout.write(f"Would delete {count} empty mailbox(es):")
            for mb in empty_mailboxes:
                self.stdout.write(f"  - {mb.address} (created {mb.created_at})")
            return
        
        # Delete the empty mailboxes
        deleted, _ = empty_mailboxes.delete()
        self.stdout.write(f"Deleted {deleted} empty mailbox(es) older than {hours} hour(s).")
