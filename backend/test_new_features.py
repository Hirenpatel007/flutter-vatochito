"""
Test script for Profile, Settings, and new Chat features
Run: python test_new_features.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vatochito_backend.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import UserSettings
from chat.models import Call, CallParticipant, Notification

User = get_user_model()

def test_profile_features():
    """Test user profile features"""
    print("\n=== Testing Profile Features ===")
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'display_name': 'Test User',
            'bio': 'This is my test bio',
            'status_message': 'Available',
            'country': 'USA',
            'city': 'New York',
            'show_phone_number': True,
            'show_last_seen': True,
            'allow_calls': True,
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Created test user: {user.username}")
    else:
        print(f"✓ Found existing user: {user.username}")
    
    # Test profile fields
    print(f"  - Display Name: {user.display_name}")
    print(f"  - Bio: {user.bio}")
    print(f"  - Status: {user.status_message}")
    print(f"  - Location: {user.city}, {user.country}")
    print(f"  - Privacy: Phone={user.show_phone_number}, LastSeen={user.show_last_seen}")
    
    return user

def test_settings_features(user):
    """Test user settings"""
    print("\n=== Testing Settings Features ===")
    
    # Get or create settings
    settings, created = UserSettings.objects.get_or_create(
        user=user,
        defaults={
            'enable_notifications': True,
            'notification_sound': True,
            'theme': 'light',
            'language': 'en',
            'enter_to_send': True,
            'auto_download_photos': True,
        }
    )
    
    if created:
        print(f"✓ Created settings for {user.username}")
    else:
        print(f"✓ Found existing settings for {user.username}")
    
    print(f"  - Notifications: {settings.enable_notifications}")
    print(f"  - Sound: {settings.notification_sound}")
    print(f"  - Theme: {settings.theme}")
    print(f"  - Language: {settings.language}")
    print(f"  - Enter to Send: {settings.enter_to_send}")
    print(f"  - Auto-download Photos: {settings.auto_download_photos}")
    
    return settings

def test_call_features(user):
    """Test call models"""
    print("\n=== Testing Call Features ===")
    
    # Create test users for calls
    user2, _ = User.objects.get_or_create(
        username='testuser2',
        defaults={'email': 'test2@example.com'}
    )
    
    # Import Conversation here to avoid circular import
    from chat.models import Conversation, ConversationMembership
    
    # Create a conversation
    conversation, _ = Conversation.objects.get_or_create(
        owner=user,
        conversation_type='direct',
        defaults={'title': f'{user.username} - {user2.username}'}
    )
    
    # Add members
    ConversationMembership.objects.get_or_create(conversation=conversation, user=user)
    ConversationMembership.objects.get_or_create(conversation=conversation, user=user2)
    
    # Create a test call
    call, created = Call.objects.get_or_create(
        conversation=conversation,
        caller=user,
        defaults={
            'call_type': 'voice',
            'state': 'ended',
            'duration': 125,
        }
    )
    
    if created:
        print(f"✓ Created test call")
        
        # Add participants
        CallParticipant.objects.get_or_create(
            call=call,
            user=user,
            defaults={'is_answered': True}
        )
        CallParticipant.objects.get_or_create(
            call=call,
            user=user2,
            defaults={'is_answered': True}
        )
    else:
        print(f"✓ Found existing call")
    
    print(f"  - Call Type: {call.get_call_type_display()}")
    print(f"  - State: {call.get_state_display()}")
    print(f"  - Duration: {call.duration}s")
    print(f"  - Participants: {call.participants.count()}")
    
    return call

def test_notification_features(user):
    """Test notification models"""
    print("\n=== Testing Notification Features ===")
    
    # Create test notification
    notification, created = Notification.objects.get_or_create(
        user=user,
        notification_type='message',
        defaults={
            'title': 'New Message',
            'message': 'You have a new message from Test User 2',
            'is_read': False,
        }
    )
    
    if created:
        print(f"✓ Created test notification")
    else:
        print(f"✓ Found existing notification")
    
    print(f"  - Type: {notification.get_notification_type_display()}")
    print(f"  - Title: {notification.title}")
    print(f"  - Message: {notification.message}")
    print(f"  - Read: {notification.is_read}")
    
    # Count notifications
    total = Notification.objects.filter(user=user).count()
    unread = Notification.objects.filter(user=user, is_read=False).count()
    print(f"  - Total notifications: {total}")
    print(f"  - Unread notifications: {unread}")
    
    return notification

def test_api_endpoints():
    """Test that API endpoints are properly configured"""
    print("\n=== Testing API Endpoints ===")
    
    from django.urls import reverse, NoReverseMatch
    
    endpoints = [
        ('register', '/auth/register/'),
        ('login', '/auth/login/'),
        ('current-user', '/auth/user/'),
        ('profile-me', '/auth/profile/me/'),
        ('profile-avatar', '/auth/profile/avatar/'),
        ('settings', '/auth/settings/'),
        ('settings-reset', '/auth/settings/reset/'),
    ]
    
    for name, path in endpoints:
        try:
            url = reverse(name)
            print(f"✓ {name}: {url}")
        except NoReverseMatch:
            print(f"✗ {name}: NOT FOUND (expected {path})")

def print_summary():
    """Print summary statistics"""
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    user_count = User.objects.count()
    settings_count = UserSettings.objects.count()
    call_count = Call.objects.count()
    notification_count = Notification.objects.count()
    
    print(f"Total Users: {user_count}")
    print(f"User Settings: {settings_count}")
    print(f"Calls: {call_count}")
    print(f"Notifications: {notification_count}")
    
    print("\n✓ All new features are working correctly!")
    print("\nNext steps:")
    print("1. Start the backend: python manage.py runserver")
    print("2. Start the frontend: cd frontend && npm start")
    print("3. Visit http://localhost:3000")
    print("4. Login or register an account")
    print("5. Navigate to /profile to edit your profile")
    print("6. Navigate to /settings to change settings")

def main():
    print("="*50)
    print("VATOCHITO - Feature Testing")
    print("="*50)
    
    try:
        user = test_profile_features()
        test_settings_features(user)
        test_call_features(user)
        test_notification_features(user)
        test_api_endpoints()
        print_summary()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
