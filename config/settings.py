"""Django settings for VoidMail."""

from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# Trust nginx proxy headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSRF trusted origins (required when behind reverse proxy)
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="http://localhost,http://127.0.0.1", cast=Csv())

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "inbox",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database

_db_url = config("DATABASE_URL", default="postgres://voidmail:voidmail@localhost:5435/voidmail")
_db_parts = _db_url.replace("postgres://", "").replace("postgresql://", "")
_user_pass, _host_db = _db_parts.split("@")
_user, _password = _user_pass.split(":")
_host_port, _dbname = _host_db.split("/")
_host_port_parts = _host_port.split(":")
_host = _host_port_parts[0]
_port = _host_port_parts[1] if len(_host_port_parts) > 1 else "5432"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": _dbname,
        "USER": _user,
        "PASSWORD": _password,
        "HOST": _host,
        "PORT": _port,
    }
}

# Cache (Redis)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://localhost:6380/0"),
    }
}

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# VoidMail settings

MAIL_DOMAIN = config("MAIL_DOMAIN", default="voidmail.local")
MAILBOX_TTL_MINUTES = config("MAILBOX_TTL_MINUTES", default=60, cast=int)
SMTP_PORT = config("SMTP_PORT", default=2525, cast=int)
