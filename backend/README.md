# Vatochito Backend

This directory contains the Django backend that powers the Vatochito multi-platform chat application.

## Features

- Django REST Framework powered API for authentication, conversations, and messaging
- JWT-based stateless auth with refresh tokens
- WebSocket real-time messaging using Django Channels and Redis
- Pluggable media storage (local, S3-compatible) with signed uploads
- Background task support through Celery for push notifications and fan-out jobs
- API schema generation via drf-spectacular

## Getting Started

1. Create a copy of `.env.example` named `.env` and fill in the secrets.
2. Install dependencies: `pip install -r requirements.txt` (recommend using a virtual environment).
3. Run database migrations: `py manage.py migrate`.
4. Start the development stack:
   - API: `py manage.py runserver`
   - Worker: `celery -A vatochito_backend worker -l info`
   - WebSocket/Redis: ensure Redis is running (see `docker-compose.yml`).

For more details, see inline comments in settings files and app modules.
