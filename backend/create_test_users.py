"""
Quick script to create two test users for real-time chat testing
Run: python create_test_users.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vatochito_backend.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_users():
    """Create two test users: alice and bob"""
    
    print("\n" + "="*50)
    print("Creating Test Users for Real-Time Chat")
    print("="*50 + "\n")
    
    users_to_create = [
        {
            'username': 'alice',
            'email': 'alice@test.com',
            'password': 'Test@123',
            'display_name': 'Alice Wonder',
            'status_message': 'Hey! I am using Vatochito 🚀'
        },
        {
            'username': 'bob',
            'email': 'bob@test.com',
            'password': 'Test@123',
            'display_name': 'Bob Builder',
            'status_message': 'Available for chat 💬'
        },
        {
            'username': 'charlie',
            'email': 'charlie@test.com',
            'password': 'Test@123',
            'display_name': 'Charlie Brown',
            'status_message': 'Testing Vatochito! 🎉'
        }
    ]
    
    created_users = []
    
    for user_data in users_to_create:
        username = user_data['username']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            # Update password in case it was changed
            user.set_password(user_data['password'])
            user.display_name = user_data['display_name']
            user.status_message = user_data['status_message']
            user.save()
            print(f"✓ Updated existing user: {username}")
        else:
            user = User.objects.create_user(
                username=username,
                email=user_data['email'],
                password=user_data['password'],
                display_name=user_data['display_name'],
                status_message=user_data['status_message']
            )
            print(f"✓ Created new user: {username}")
        
        created_users.append(user)
    
    print("\n" + "="*50)
    print("Test Users Created Successfully!")
    print("="*50 + "\n")
    
    print("📋 Login Credentials:\n")
    for user_data in users_to_create:
        print(f"Username: {user_data['username']}")
        print(f"Password: {user_data['password']}")
        print(f"Email:    {user_data['email']}")
        print(f"Name:     {user_data['display_name']}")
        print()
    
    print("="*50)
    print("🧪 How to Test Real-Time Chat:")
    print("="*50 + "\n")
    
    print("1. Start the servers:")
    print("   - Backend:  python manage.py runserver")
    print("   - Frontend: cd frontend && npm start\n")
    
    print("2. Open TWO browsers:")
    print("   - Browser 1: http://localhost:3000")
    print("   - Browser 2: http://localhost:3000 (incognito)\n")
    
    print("3. Login:")
    print("   - Browser 1: Login as 'alice' (password: Test@123)")
    print("   - Browser 2: Login as 'bob' (password: Test@123)\n")
    
    print("4. Start chatting:")
    print("   - In Browser 1: Click 'New Chat' → Search 'bob'")
    print("   - Send message: 'Hi Bob! 🚀'")
    print("   - In Browser 2: See message appear instantly!")
    print("   - Reply from Bob")
    print("   - See real-time typing indicators\n")
    
    print("✨ Features to test:")
    print("   - Instant message delivery")
    print("   - Typing indicators ('alice is typing...')")
    print("   - Online/offline status")
    print("   - Read receipts (✓✓)")
    print("   - Multiple conversations")
    print("   - Message timestamps")
    print("   - User profiles (/profile)")
    print("   - Settings (/settings)\n")
    
    print("="*50)
    print("🎉 Ready to test! Open two browsers now!")
    print("="*50 + "\n")

if __name__ == '__main__':
    try:
        create_test_users()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
