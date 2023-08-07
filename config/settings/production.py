# -*- coding: utf-8 -*-
'''
Production Configurations

- Use sentry for error logging
'''

import logging
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .common import *  # noqa


SECRET_KEY = env("DJANGO_SECRET_KEY")

# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    },
    "file_resubmit": {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        "LOCATION": '/tmp/file_resubmit/'
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s',
        },
        'simple': {
            'format': '[%(asctime)s] %(message)s'
        },
    },
    "handlers": {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        # Errors logged by the SDK itself
        "sentry_sdk": {"level": "ERROR", "handlers": ["console"], "propagate": False},
    },
}


# Sentry
# ------------------------------------------------------------------------------
SENTRY_DSN = env("DJANGO_SENTRY_DSN")
SENTRY_LOG_LEVEL = env.int("DJANGO_SENTRY_LOG_LEVEL", logging.INFO)

sentry_logging = LoggingIntegration(
    level=SENTRY_LOG_LEVEL,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR,  # Send errors as events
)

sentry_sdk.init(
    dsn=SENTRY_DSN, 
    integrations=[sentry_logging, DjangoIntegration()],
    send_default_pii=True,
    traces_sample_rate=0.1,
)

INVITATION_VALID_DAYS = 365

INSTALLED_APPS += ("gunicorn", "email_obfuscator")

DATABASES['default'] = env.db("DATABASE_URL")

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['isimip.org'])

FILE_UPLOAD_MAX_MEMORY_SIZE = 1073741824

BASE_URL = 'https://www.isimip.org'
