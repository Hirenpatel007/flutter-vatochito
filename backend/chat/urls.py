from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import ConversationViewSet, MessageViewSet, ContactViewSet, UserSearchViewSet, download_attachment, CallViewSet

router = DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"contacts", ContactViewSet, basename="contact")
router.register(r"calls", CallViewSet, basename="call")

# Nested router for messages under conversations
conversations_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

# User search viewset
user_search_list = UserSearchViewSet.as_view({'get': 'list'})

urlpatterns = [
    path("", include(router.urls)),
    path("", include(conversations_router.urls)),
    path("users/search/", user_search_list, name="user-search"),
    path("attachments/<int:attachment_id>/download/", download_attachment, name="attachment-download"),
]

