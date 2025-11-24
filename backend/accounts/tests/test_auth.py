from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_user(self):
        payload = {
            "username": "testuser",
            "email": "user@example.com", 
            "password": "TestPassword123",
            "password2": "TestPassword123",  # Add confirm password
        }
        response = self.client.post(reverse("register"), payload)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="testuser").exists())
