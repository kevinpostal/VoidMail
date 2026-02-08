.PHONY: help install run smtp cleanup purge-empty purge-empty-dry build up down quickdev migrate makemigrations adddomain listdomains superuser

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
	@echo "    make up              Start containers (creates volume if needed)"
	@echo "    make down            Stop containers"
	@echo "    make create-volume   Create the database volume manually"
	@echo "    make backup-db       Backup database to SQL file"
	@echo "    make restore-db      Restore database from SQL file"
	@echo ""
	@echo "  Maintenance:"
	@echo "    make cleanup         Run cleanup task (remove expired mailboxes)"
	@echo "    make purge-empty     Purge empty mailboxes older than 1 hour"
	@echo "    make purge-empty-dry Preview empty mailboxes to be purged"
	@echo "    make superuser       Create Django superuser account"

install:
	uv sync

run:
	uv run granian config.asgi:application --interface asgi --host 0.0.0.0 --port 8005 --reload

smtp:
	uv run python manage.py smtpserver

cleanup:
	uv run python manage.py cleanup --once

purge-empty:
	uv run python manage.py purge_empty_mailboxes

purge-empty-dry:
	uv run python manage.py purge_empty_mailboxes --dry-run

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

create-volume:
	podman volume exists voidmail_pgdata || podman volume create voidmail_pgdata
	@echo "Volume voidmail_pgdata is ready"

# For first-time setup, run: make create-volume && make up

down:
	podman compose down 2>/dev/null || true

# NEVER use -v flag with down - it removes all volumes and data!
# The volume is now marked as 'external' in compose.yaml to prevent deletion.

# WARNING: This will DESTROY ALL DATA including the database volume
reset-everything:
	@echo "WARNING: This will DELETE ALL DATA including the database volume!"
	@echo "Are you sure? Type 'yes' to continue: "
	@read confirm && [ "$$confirm" = "yes" ] && podman compose down -v || echo "Aborted"

backup-db:
	podman exec voidmail-db-1 pg_dump -U voidmail voidmail > backup_$$(date +%Y%m%d_%H%M%S).sql

restore-db:
	@echo "Usage: make restore-db FILE=backup_YYYYMMDD_HHMMSS.sql"
	[ -n "$(FILE)" ] && podman exec -i voidmail-db-1 psql -U voidmail voidmail < $(FILE)

quickdev: install migrate run

adddomain:
	uv run python manage.py adddomain $(DOMAIN)

listdomains:
	uv run python manage.py listdomains

superuser:
	uv run python manage.py createsuperuser
