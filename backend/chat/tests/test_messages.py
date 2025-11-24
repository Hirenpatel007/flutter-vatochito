from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from chat.models import Conversation, ConversationMembership

User = get_user_model()


class MessageTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="sender", password="pass12345")
        self.other = User.objects.create_user(username="receiver", password="pass12345")
        self.conversation = Conversation.objects.create(owner=self.user)
        ConversationMembership.objects.create(conversation=self.conversation, user=self.user)
        ConversationMembership.objects.create(conversation=self.conversation, user=self.other)

    def test_send_message(self):
        self.client.force_authenticate(user=self.user)  # Use token auth instead of login
        url = reverse("conversation-messages-list", kwargs={"conversation_pk": self.conversation.id})
        response = self.client.post(url, {"content": "Hello"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["content"], "Hello")
