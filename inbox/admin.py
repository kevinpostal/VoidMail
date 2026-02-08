from django.contrib import admin

from .models import Domain, Email, Mailbox


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name",)


@admin.register(Mailbox)
class MailboxAdmin(admin.ModelAdmin):
    list_display = ("address", "domain", "created_at", "expires_at", "is_expired")
    readonly_fields = ("token",)
    list_filter = ("domain", "created_at")


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "subject", "received_at", "size_bytes")
    list_filter = ("received_at",)
