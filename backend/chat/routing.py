from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/chat/<int:conversation_id>/", consumers.ConversationConsumer.as_asgi()),
]
