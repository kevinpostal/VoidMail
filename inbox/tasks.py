"""Scheduled tasks for VoidMail."""

from datetime import timedelta

from django.tasks import task
from django_scheduled_tasks.base import periodic_task


@task
def purge_empty_mailboxes_task(hours: int = 1) -> str:
    """Task to purge empty mailboxes older than specified hours."""
    from django.core.management import call_command
    from django.utils import timezone
    
    call_command("purge_empty_mailboxes", hours=hours)
    return f"Purge completed at {timezone.now()}"


# Register the task to run every hour
periodic_task(
    interval=timedelta(hours=1),
    task=purge_empty_mailboxes_task,
)
