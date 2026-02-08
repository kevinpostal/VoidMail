"""SMTP server that receives emails and stores them in the database."""

import asyncio
import email
import email.policy
import logging

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP as SMTPServer

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from inbox.models import Domain, Email, Mailbox

logger = logging.getLogger("voidmail.smtp")


class VoidMailHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        domain = address.split("@")[-1].lower()
        # Check if domain is active in our database
        domain_exists = await Domain.objects.filter(name__iexact=domain, is_active=True).aexists()
        if not domain_exists:
            return f"550 not relaying to {domain}"
        envelope.rcpt_tos.append(address)
        return "250 OK"

    async def handle_DATA(self, server, session, envelope):
        raw = envelope.content
        if isinstance(raw, bytes):
            raw_str = raw.decode("utf-8", errors="replace")
        else:
            raw_str = raw

        msg = email.message_from_string(raw_str, policy=email.policy.default)
        sender = envelope.mail_from or msg.get("From", "unknown@unknown")
        subject = msg.get("Subject", "(no subject)") or "(no subject)"

        body_text = ""
        body_html = ""

        if msg.is_multipart():
            for part in msg.walk():
                ct = part.get_content_type()
                if ct == "text/plain" and not body_text:
                    body_text = part.get_content()
                elif ct == "text/html" and not body_html:
                    body_html = part.get_content()
        else:
            ct = msg.get_content_type()
            content = msg.get_content()
            if ct == "text/html":
                body_html = content
            else:
                body_text = content

        size_bytes = len(raw) if isinstance(raw, bytes) else len(raw.encode("utf-8"))

        for recipient in envelope.rcpt_tos:
            try:
                mailbox = await Mailbox.objects.aget(
                    address__iexact=recipient,
                    expires_at__gt=timezone.now(),
                )
                await Email.objects.acreate(
                    mailbox=mailbox,
                    sender=sender,
                    recipient=recipient,
                    subject=subject[:998],
                    body_text=body_text,
                    body_html=body_html,
                    size_bytes=size_bytes,
                )
                logger.info("Stored email from %s to %s: %s", sender, recipient, subject)
            except Mailbox.DoesNotExist:
                logger.debug("Discarded email for unknown/expired address: %s", recipient)

        return "250 Message accepted"


class Command(BaseCommand):
    help = "Run the SMTP server to receive incoming emails"

    def add_arguments(self, parser):
        parser.add_argument(
            "--port", type=int, default=None,
            help=f"Port to listen on (default: SMTP_PORT from settings)",
        )
        parser.add_argument(
            "--host", type=str, default="0.0.0.0",
            help="Host to bind to (default: 0.0.0.0)",
        )

    def handle(self, *args, **options):
        port = options["port"] or settings.SMTP_PORT
        host = options["host"]

        self.stdout.write(f"Starting SMTP server on {host}:{port}")
        self.stdout.write(f"Accepting mail for configured domains")

        handler = VoidMailHandler()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        server = Controller(
            handler,
            hostname=host,
            port=port,
        )
        server.start()
        self.stdout.write(self.style.SUCCESS(f"SMTP server listening on {host}:{port}"))

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self.stdout.write("\nShutting down SMTP server...")
        finally:
            server.stop()
