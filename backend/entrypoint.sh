#!/bin/sh
set -e

# Default to production settings if not set
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-vatochito_backend.settings.production}

# Ensure logs directory exists for Django file handlers
mkdir -p /code/logs

# Run migrations
python manage.py migrate --noinput

# Create a superuser if one doesn't exist
python manage.py createsu

# Create static files (already collected at build; repeat to be safe on new releases)
python manage.py collectstatic --noinput || true

# Start ASGI server with Daphne for WebSockets
exec daphne -b 0.0.0.0 -p 8000 vatochito_backend.asgi:application
