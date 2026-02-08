from django.apps import AppConfig


class InboxConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "inbox"

    def ready(self):
        # Import tasks to register them with the scheduler
        import inbox.tasks  # noqa: F401
