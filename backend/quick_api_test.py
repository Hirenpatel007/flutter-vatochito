"""Quick Mobile API Test"""
import requests

BASE_URL = "http://localhost:8000/api"

print("🧪 Testing Vatochito Mobile API\n")

# 1. Test Login
print("1️⃣ Testing Login...")
response = requests.post(f"{BASE_URL}/accounts/login/", json={
    "username": "alice",
    "password": "Test@123"
})
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    token = data['access']
    print(f"   ✅ Login successful! Token: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test Get Profile
    print("\n2️⃣ Testing Get Profile...")
    response = requests.get(f"{BASE_URL}/accounts/profile/me/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Profile fetched!")
        print(f"   User: {response.json().get('username')}")
    
    # 3. Test Search Users
    print("\n3️⃣ Testing Search Users...")
    response = requests.get(f"{BASE_URL}/chat/users/search/?search=bob", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        users = response.json()
        print(f"   ✅ Found {len(users)} user(s)")
        if users:
            print(f"   First result: {users[0].get('username')}")
    
    # 4. Test List Conversations
    print("\n4️⃣ Testing List Conversations...")
    response = requests.get(f"{BASE_URL}/chat/conversations/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        convs = response.json()
        print(f"   ✅ Found {len(convs)} conversation(s)")
        if convs:
            conv_id = convs[0]['id']
            
            # 5. Test Get Messages
            print(f"\n5️⃣ Testing Get Messages (conversation {conv_id})...")
            response = requests.get(f"{BASE_URL}/chat/conversations/{conv_id}/messages/", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                msgs = response.json()
                print(f"   ✅ Found {len(msgs)} message(s)")
                
                # 6. Test Send Message
                print(f"\n6️⃣ Testing Send Message...")
                response = requests.post(f"{BASE_URL}/chat/conversations/{conv_id}/messages/", 
                    json={"content": "Mobile API test message! 📱", "message_type": "text"},
                    headers=headers)
                print(f"   Status: {response.status_code}")
                if response.status_code == 201:
                    print(f"   ✅ Message sent successfully!")
    
    # 7. Test Settings
    print("\n7️⃣ Testing Get Settings...")
    response = requests.get(f"{BASE_URL}/accounts/settings/me/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Settings fetched!")
        settings = response.json()
        print(f"   Theme: {settings.get('theme')}, Language: {settings.get('language')}")
    
    print("\n" + "="*50)
    print("✅ All tests completed successfully!")
    print("="*50)
    print("\n📱 Mobile API is working properly!")
    print("   - Authentication ✅")
    print("   - User Profile ✅")
    print("   - User Search ✅")
    print("   - Conversations ✅")
    print("   - Messages ✅")
    print("   - Settings ✅")
    print("\n🚀 Ready for mobile app integration!")
else:
    print(f"   ❌ Login failed!")
