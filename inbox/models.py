import secrets
import string
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_token():
    return secrets.token_urlsafe(32)


def generate_local_part():
    """Generate the local part (before @) of the email address."""
    chars = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(10))


def default_expiry():
    return timezone.now() + timedelta(minutes=settings.MAILBOX_TTL_MINUTES)


class Domain(models.Model):
    """Email domains supported by the service."""

    name = models.CharField(max_length=253, unique=True, help_text="Domain name (e.g., voidmail.local)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Mailbox(models.Model):
    address = models.EmailField(unique=True)
    domain = models.ForeignKey(
        Domain,
        on_delete=models.CASCADE,
        related_name="mailboxes",
        null=True,
        blank=True,
    )
    token = models.CharField(max_length=64, unique=True, default=generate_token)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiry)

    class Meta:
        verbose_name_plural = "mailboxes"

    def __str__(self):
        return self.address

    def save(self, *args, **kwargs):
        # Auto-generate address if not set
        if not self.address:
            if not self.domain_id:
                # Get or create the default domain from settings
                default_domain_name = getattr(settings, "MAIL_DOMAIN", "voidmail.local")
                self.domain, _ = Domain.objects.get_or_create(
                    name=default_domain_name,
                    defaults={"is_active": True},
                )
            self.address = f"{generate_local_part()}@{self.domain.name}"
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at


class Email(models.Model):
    mailbox = models.ForeignKey(Mailbox, on_delete=models.CASCADE, related_name="emails")
    sender = models.EmailField()
    recipient = models.EmailField()
    subject = models.CharField(max_length=998, default="(no subject)")
    body_text = models.TextField(blank=True, default="")
    body_html = models.TextField(blank=True, default="")
    received_at = models.DateTimeField(auto_now_add=True)
    size_bytes = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False, help_text="Soft delete - hidden from UI but kept in database")

    class Meta:
        ordering = ["-received_at"]

    def __str__(self):
        return f"{self.sender} → {self.subject}"
