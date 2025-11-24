"""
Quick test script to verify registration endpoint
Run with: python test_registration.py
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_registration():
    """Test user registration"""
    print("Testing registration endpoint...")
    
    data = {
        "username": "testuser2",
        "password": "testpass123",
        "email": "testuser2@vatochito.local"
    }
    
    print(f"\nSending POST to {BASE_URL}/api/auth/")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            print("\n✅ Registration successful!")
            tokens = response.json()
            print(f"Access Token: {tokens.get('access', 'N/A')[:50]}...")
            print(f"Refresh Token: {tokens.get('refresh', 'N/A')[:50]}...")
        else:
            print(f"\n❌ Registration failed!")
            try:
                errors = response.json()
                print(f"Errors: {json.dumps(errors, indent=2)}")
            except:
                print(f"Raw response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to Django server!")
        print("Make sure the server is running: python manage.py runserver")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_registration()
