from django.urls import path

from chat import routing as chat_routing

websocket_urlpatterns = [
    *chat_routing.websocket_urlpatterns,
]
