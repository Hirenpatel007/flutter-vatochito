"""
Quick test script for authentication
Usage: python quick_test.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vatochito_backend.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import json

User = get_user_model()

def test_auth():
    client = APIClient()
    
    print("\n" + "="*60)
    print("AUTHENTICATION TEST")
    print("="*60)
    
    # Clean up test user if exists
    User.objects.filter(username='testuser').delete()
    
    # Test 1: Register
    print("\n1. Testing Registration...")
    register_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'password2': 'testpass123',
        'display_name': 'Test User',
        'phone_number': '+1234567890'
    }
    
    response = client.post('/api/auth/register/', register_data, format='json')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ Registration successful!")
        tokens = response.json()
        access_token = tokens.get('access')
        refresh_token = tokens.get('refresh')
    else:
        print("❌ Registration failed!")
        return
    
    # Test 2: Login
    print("\n2. Testing Login...")
    login_data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    
    response = client.post('/api/auth/login/', login_data, format='json')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
        tokens = response.json()
        access_token = tokens.get('access')
    else:
        print("❌ Login failed!")
        return
    
    # Test 3: Get current user
    print("\n3. Testing Get Current User...")
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    response = client.get('/api/auth/user/')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Get user successful!")
    else:
        print("❌ Get user failed!")
    
    # Test 4: Update user
    print("\n4. Testing Update User...")
    update_data = {
        'status_message': 'Testing status update!'
    }
    response = client.patch('/api/auth/user/', update_data, format='json')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Update user successful!")
    else:
        print("❌ Update user failed!")
    
    # Test 5: Token refresh
    print("\n5. Testing Token Refresh...")
    refresh_data = {
        'refresh': refresh_token
    }
    response = client.post('/api/auth/token/refresh/', refresh_data, format='json')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Token refresh successful!")
    else:
        print("❌ Token refresh failed!")
    
    print("\n" + "="*60)
    print("TEST COMPLETE!")
    print("="*60)

if __name__ == '__main__':
    test_auth()
