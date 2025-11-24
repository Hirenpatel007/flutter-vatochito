"""
Production Configuration & Deployment Guide
============================================

This file contains all settings and configurations needed for production deployment.
"""

# Environment-specific settings
PRODUCTION_SETTINGS = {
    'DEBUG': False,
    'ALLOWED_HOSTS': ['your-domain.com', 'www.your-domain.com'],
    'SECURE_SSL_REDIRECT': True,
    'SECURE_HSTS_SECONDS': 31536000,  # 1 year
    'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
    'SECURE_HSTS_PRELOAD': True,
    'SESSION_COOKIE_SECURE': True,
    'CSRF_COOKIE_SECURE': True,
    'SECURE_BROWSER_XSS_FILTER': True,
    'SECURE_CONTENT_TYPE_NOSNIFF': True,
    'X_FRAME_OPTIONS': 'DENY',
}

# Database Configuration (PostgreSQL recommended for production)
DATABASE_CONFIG = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'vatochito_db',
    'USER': 'vatochito_user',
    'PASSWORD': 'CHANGE_THIS_PASSWORD',
    'HOST': 'localhost',
    'PORT': '5432',
    'CONN_MAX_AGE': 600,  # Connection pooling
    'OPTIONS': {
        'connect_timeout': 10,
    }
}

# Redis Configuration (Required for WebSocket in production)
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': 'CHANGE_THIS_PASSWORD',
}

# Celery Configuration (for background tasks)
CELERY_CONFIG = {
    'broker_url': 'redis://localhost:6379/1',
    'result_backend': 'redis://localhost:6379/2',
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'Asia/Kolkata',
    'enable_utc': True,
}

# Email Configuration (for production)
EMAIL_CONFIG = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.gmail.com',  # Or your email service
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'your-email@gmail.com',
    'EMAIL_HOST_PASSWORD': 'your-app-password',
    'DEFAULT_FROM_EMAIL': 'Vatochito <noreply@your-domain.com>',
}

# AWS S3 Configuration (for media files)
AWS_CONFIG = {
    'AWS_ACCESS_KEY_ID': 'YOUR_ACCESS_KEY',
    'AWS_SECRET_ACCESS_KEY': 'YOUR_SECRET_KEY',
    'AWS_STORAGE_BUCKET_NAME': 'vatochito-media',
    'AWS_S3_REGION_NAME': 'ap-south-1',  # Mumbai region
    'AWS_S3_CUSTOM_DOMAIN': f'vatochito-media.s3.amazonaws.com',
    'AWS_DEFAULT_ACL': 'public-read',
    'AWS_QUERYSTRING_AUTH': False,
    'AWS_S3_OBJECT_PARAMETERS': {
        'CacheControl': 'max-age=86400',
    },
}

# Static & Media Files
STATIC_ROOT = '/var/www/vatochito/static/'
MEDIA_ROOT = '/var/www/vatochito/media/'

# CORS Settings (for production)
CORS_CONFIG = {
    'CORS_ALLOWED_ORIGINS': [
        'https://your-domain.com',
        'https://www.your-domain.com',
    ],
    'CORS_ALLOW_CREDENTIALS': True,
}

# Rate Limiting (prevent abuse)
RATE_LIMIT_CONFIG = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'message': '100/minute',
        'login': '5/minute',
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/vatochito/django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/vatochito/errors.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'chat': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# WebSocket Configuration
WEBSOCKET_CONFIG = {
    'CHANNEL_LAYERS': {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [('localhost', 6379)],
                'capacity': 1500,
                'expiry': 10,
            },
        },
    },
}

# Backup Settings
BACKUP_CONFIG = {
    'DATABASE_BACKUP_DIR': '/var/backups/vatochito/db/',
    'MEDIA_BACKUP_DIR': '/var/backups/vatochito/media/',
    'BACKUP_RETENTION_DAYS': 30,
}

# Monitoring & Performance
MONITORING_CONFIG = {
    'SENTRY_DSN': 'https://your-sentry-dsn@sentry.io/project',
    'SENTRY_TRACES_SAMPLE_RATE': 0.1,
}
