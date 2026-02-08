from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Domain, Email, Mailbox


def home(request):
    """Auto-create a mailbox and redirect to inbox — tempmail-style instant start."""
    domain = Domain.objects.filter(is_active=True).first()
    mailbox = Mailbox.objects.create(domain=domain)
    return redirect("inbox:inbox_view", token=mailbox.token)


@require_POST
def create_mailbox(request):
    """Create a mailbox with optional custom name and domain."""
    domain_id = request.POST.get("domain")
    name = request.POST.get("name", "").strip().lower()

    domain = None
    if domain_id:
        domain = get_object_or_404(Domain, id=domain_id, is_active=True)
    else:
        domain = Domain.objects.filter(is_active=True).first()

    if name:
        address = f"{name}@{domain.name}"
        # Check if address is taken by a non-expired mailbox
        existing = Mailbox.objects.filter(address=address, expires_at__gt=timezone.now()).first()
        if existing:
            return redirect("inbox:inbox_view", token=existing.token)
        # Clean up any expired mailbox with this address
        Mailbox.objects.filter(address=address, expires_at__lte=timezone.now()).delete()
        mailbox = Mailbox(domain=domain, address=address)
        mailbox.save()
    else:
        mailbox = Mailbox.objects.create(domain=domain)

    return redirect("inbox:inbox_view", token=mailbox.token)


def inbox_view(request, token):
    """Display the inbox for a mailbox."""
    mailbox = get_object_or_404(Mailbox, token=token)
    emails = mailbox.emails.filter(is_deleted=False)
    now = timezone.now()
    remaining = max(0, int((mailbox.expires_at - now).total_seconds()))

    # Split address into local part and domain for the editable input
    local_part, _ = mailbox.address.split("@", 1)

    domains = Domain.objects.filter(is_active=True)

    return render(request, "inbox/inbox.html", {
        "mailbox": mailbox,
        "emails": emails,
        "remaining_seconds": remaining,
        "domains": domains,
        "local_part": local_part,
    })


def check_emails(request, token):
    """JSON polling endpoint — returns new email count and list."""
    mailbox = get_object_or_404(Mailbox, token=token)
    if mailbox.is_expired:
        return JsonResponse({"expired": True, "emails": []})

    since = request.GET.get("since")
    emails = mailbox.emails.filter(is_deleted=False)
    if since:
        try:
            from datetime import datetime
            since_dt = datetime.fromisoformat(since)
            emails = emails.filter(received_at__gt=since_dt)
        except (ValueError, TypeError):
            pass

    return JsonResponse({
        "expired": False,
        "count": mailbox.emails.count(),
        "emails": [
            {
                "id": e.id,
                "sender": e.sender,
                "subject": e.subject,
                "received_at": e.received_at.isoformat(),
            }
            for e in emails[:50]
        ],
    })


@require_POST
def new_mailbox(request):
    """Create a fresh mailbox and redirect."""
    domain_id = request.POST.get("domain")
    if domain_id:
        domain = get_object_or_404(Domain, id=domain_id, is_active=True)
        mailbox = Mailbox.objects.create(domain=domain)
    else:
        mailbox = Mailbox.objects.create()
    return redirect("inbox:inbox_view", token=mailbox.token)


def email_detail(request, pk):
    """View a single email."""
    email = get_object_or_404(Email, pk=pk, is_deleted=False)
    mailbox = email.mailbox
    return render(request, "inbox/email_detail.html", {
        "email": email,
        "mailbox": mailbox,
    })


@require_POST
def delete_email(request, pk):
    """Soft delete a single email (mark as hidden) and redirect back to inbox."""
    email = get_object_or_404(Email, pk=pk)
    mailbox = email.mailbox
    email.is_deleted = True
    email.save()
    return redirect("inbox:inbox_view", token=mailbox.token)


def health_check(request):
    """Health check endpoint."""
    return JsonResponse({"status": "ok"})
