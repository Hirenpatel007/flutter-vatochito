"""
Quick test to verify search endpoint URL
Run after starting server: python test_search_endpoint.py
"""

import requests

def test_search_endpoint():
    print("\n" + "="*50)
    print("Testing Search Endpoint URL")
    print("="*50 + "\n")
    
    # First, let's try to login and get a token
    print("Step 1: Login to get access token...")
    
    login_url = "http://localhost:8000/api/auth/login/"
    login_data = {
        "username": "alice",
        "password": "Test@123"
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access')
            print(f"✓ Login successful! Got access token")
            
            # Now test the search endpoint
            print("\nStep 2: Testing search endpoint...")
            search_url = "http://localhost:8000/api/chat/users/search/"
            headers = {"Authorization": f"Bearer {access_token}"}
            params = {"q": "bob"}
            
            response = requests.get(search_url, headers=headers, params=params)
            print(f"\nURL: {response.url}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                users = response.json()
                print(f"✓ Search working! Found {len(users)} users")
                for user in users:
                    print(f"  - {user['username']} ({user.get('display_name', 'No name')})")
            else:
                print(f"✗ Error: {response.status_code}")
                print(f"Response: {response.text}")
        else:
            print(f"✗ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            print("\nMake sure:")
            print("1. Backend is running: python manage.py runserver")
            print("2. User 'alice' exists with password 'Test@123'")
            print("   Run: python create_test_users.py")
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend!")
        print("\nPlease start the backend server:")
        print("  cd backend")
        print("  python manage.py runserver")
        return
    
    print("\n" + "="*50)
    print("Test Complete!")
    print("="*50 + "\n")

if __name__ == '__main__':
    test_search_endpoint()
