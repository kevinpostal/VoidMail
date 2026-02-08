.PHONY: help install run smtp cleanup build up down quickdev migrate makemigrations adddomain listdomains superuser

TO ?= test@voidmail.local
FROM ?= sender@example.com

help:
	@echo "VoidMail — Available Commands:"
	@echo ""
	@echo "  Development:"
	@echo "    make install         Install dependencies with uv"
	@echo "    make run             Run Django development server"
	@echo "    make smtp            Run SMTP server"
	@echo "    make quickdev        Install, migrate, and run (full dev setup)"
	@echo ""
	@echo "  Database:"
	@echo "    make migrate         Apply database migrations"
	@echo "    make makemigrations  Create new migrations"
	@echo ""
	@echo "  Domain Management:"
	@echo "    make adddomain DOMAIN=example.com  Add a new email domain"
	@echo "    make listdomains                   List all configured domains"
	@echo ""
	@echo "  Testing:"
	@echo "    make test-email [TO=addr@domain] [FROM=sender@domain]"
	@echo "                         Send a test email via swaks"
	@echo ""
	@echo "  Containers:"
	@echo "    make build           Build Podman containers"
	@echo "    make up              Start containers"
	@echo "    make down            Stop containers"
	@echo ""
	@echo "  Maintenance:"
	@echo "    make cleanup         Run cleanup task (remove expired mailboxes)"
	@echo "    make superuser       Create Django superuser account"

install:
	uv sync

run:
	uv run granian config.asgi:application --interface asgi --host 0.0.0.0 --port 8005 --reload

smtp:
	uv run python manage.py smtpserver

cleanup:
	uv run python manage.py cleanup --once

migrate:
	uv run python manage.py migrate

makemigrations:
	uv run python manage.py makemigrations

test-email:
	podman exec voidmail-smtp-1 swaks --to $(TO) --from $(FROM) --server localhost:2525 --body "This is a test email from swaks inside the container." --header "Subject: Swaks Container Test"

build:
	podman compose build

up:
	podman compose up -d

down:
	podman compose down

quickdev: install migrate run

adddomain:
	uv run python manage.py adddomain $(DOMAIN)

listdomains:
	uv run python manage.py listdomains

superuser:
	uv run python manage.py createsuperuser
