"""
Simple script to create a direct conversation between lalo and kalu
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

# Login as lalo
print("1. Logging in as lalo...")
response = requests.post(
    f"{BASE_URL}/api/auth/login/",
    json={"username": "lalo", "password": "lalo123"}
)
if response.status_code == 200:
    lalo_token = response.json()["access"]
    print(f"✅ Logged in as lalo")
else:
    print(f"❌ Failed to login as lalo: {response.text}")
    exit(1)

# Get lalo's user details
print("\n2. Getting lalo's profile...")
response = requests.get(
    f"{BASE_URL}/api/auth/profile/me/",
    headers={"Authorization": f"Bearer {lalo_token}"}
)
lalo_user = response.json()
print(f"✅ Lalo ID: {lalo_user['id']}")

# Login as kalu to get their ID
print("\n3. Logging in as kalu...")
response = requests.post(
    f"{BASE_URL}/api/auth/login/",
    json={"username": "kalu", "password": "kalu123"}
)
if response.status_code == 200:
    kalu_token = response.json()["access"]
    print(f"✅ Logged in as kalu")
else:
    print(f"❌ Failed to login as kalu: {response.text}")
    exit(1)

# Get kalu's user details
print("\n4. Getting kalu's profile...")
response = requests.get(
    f"{BASE_URL}/api/auth/profile/me/",
    headers={"Authorization": f"Bearer {kalu_token}"}
)
kalu_user = response.json()
print(f"✅ Kalu ID: {kalu_user['id']}")

# Create conversation as lalo with kalu
print(f"\n5. Creating conversation between lalo and kalu...")
response = requests.post(
    f"{BASE_URL}/api/chat/conversations/create-direct/",
    json={"user_id": kalu_user['id']},
    headers={"Authorization": f"Bearer {lalo_token}"}
)
if response.status_code in [200, 201]:
    conversation = response.json()
    print(f"✅ Conversation created: ID={conversation['id']}")
    print(f"   Members: {len(conversation['members'])} users")
else:
    print(f"❌ Failed to create conversation: {response.status_code}")
    print(f"   Response: {response.text}")

# Verify both users can see the conversation
print("\n6. Checking lalo's conversations...")
response = requests.get(
    f"{BASE_URL}/api/chat/conversations/",
    headers={"Authorization": f"Bearer {lalo_token}"}
)
lalo_convs = response.json()
print(f"✅ Lalo sees {len(lalo_convs)} conversations")

print("\n7. Checking kalu's conversations...")
response = requests.get(
    f"{BASE_URL}/api/chat/conversations/",
    headers={"Authorization": f"Bearer {kalu_token}"}
)
kalu_convs = response.json()
print(f"✅ Kalu sees {len(kalu_convs)} conversations")

print("\n🎉 Done! Both users should now be able to chat.")
