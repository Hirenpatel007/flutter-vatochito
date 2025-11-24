FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
		PYTHONUNBUFFERED=1 \
		DJANGO_SETTINGS_MODULE=vatochito_backend.settings.production

WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
		build-essential \
		libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static at build time to speed up cold starts (safe with WhiteNoise)
# Ensure logs directory exists before any Django commands (logging handlers)
RUN mkdir -p /code/logs

# Collect static files (won't fail build if settings defer)
RUN python manage.py collectstatic --noinput || true

# Expose the port Render will connect to
EXPOSE 8000

# Entrypoint runs migrations then starts Daphne (ASGI) for WebSockets
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
