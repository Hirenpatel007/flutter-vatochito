#!/usr/bin/env python
"""
Test script to verify authentication endpoints
Run with: python test_auth_endpoints.py
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/auth"

def test_register():
    """Test user registration"""
    print("\n=== Testing Registration ===")
    url = f"{BASE_URL}/register/"
    data = {
        "username": "testuser123",
        "email": "test@example.com",
        "password": "testpass123",
        "display_name": "Test User",
        "phone_number": "+1234567890"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return response.json()
        else:
            print("❌ Registration failed!")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_login(username, password):
    """Test user login"""
    print("\n=== Testing Login ===")
    url = f"{BASE_URL}/login/"
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json()
        else:
            print("❌ Login failed!")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_get_user(access_token):
    """Test getting current user"""
    print("\n=== Testing Get Current User ===")
    url = f"{BASE_URL}/user/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Get user successful!")
            return response.json()
        else:
            print("❌ Get user failed!")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    print("=" * 50)
    print("Authentication Endpoints Test")
    print("=" * 50)
    
    # Test registration
    register_result = test_register()
    
    if register_result and "access" in register_result:
        # Test get current user with token from registration
        test_get_user(register_result["access"])
    
    # Test login
    login_result = test_login("testuser123", "testpass123")
    
    if login_result and "access" in login_result:
        # Test get current user with token from login
        test_get_user(login_result["access"])
    
    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
