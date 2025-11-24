import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vatochito_backend.settings.development")

django_asgi_app = get_asgi_application()

from . import routing  # noqa: E402  pylint: disable=wrong-import-position
from chat.middleware import JWTAuthMiddleware  # noqa: E402  pylint: disable=wrong-import-position

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(URLRouter(routing.websocket_urlpatterns)),
    }
)
