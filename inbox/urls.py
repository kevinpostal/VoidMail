from django.urls import path

from . import views

app_name = "inbox"

urlpatterns = [
    path("", views.home, name="home"),
    path("create/", views.create_mailbox, name="create_mailbox"),
    path("inbox/<str:token>/", views.inbox_view, name="inbox_view"),
    path("inbox/<str:token>/check/", views.check_emails, name="check_emails"),
    path("email/<int:pk>/", views.email_detail, name="email_detail"),
    path("new/", views.new_mailbox, name="new_mailbox"),
    path("health/", views.health_check, name="health_check"),
]
