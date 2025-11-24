#!/usr/bin/env python
"""
Generate 500 realistic test users for performance testing
Creates users with:
- Realistic names
- Random avatars (from external API)
- Bio/status messages
- Different online status
"""
import os
import sys
import django
import random

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vatochito_backend.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import UserSettings

User = get_user_model()

# Indian/Common names
FIRST_NAMES = [
    'Rahul', 'Priya', 'Amit', 'Sneha', 'Raj', 'Anjali', 'Vikram', 'Pooja', 
    'Arjun', 'Neha', 'Rohan', 'Kavita', 'Sanjay', 'Divya', 'Anil', 'Ritu',
    'Kunal', 'Meera', 'Vishal', 'Shruti', 'Nikhil', 'Anita', 'Deepak', 'Swati',
    'Gaurav', 'Preeti', 'Ashish', 'Nisha', 'Manish', 'Rekha', 'Suresh', 'Geeta',
    'Ramesh', 'Sunita', 'Karan', 'Isha', 'Jay', 'Riya', 'Dev', 'Maya',
    'Harsh', 'Simran', 'Yash', 'Tara', 'Aditya', 'Diya', 'Vivek', 'Rani',
    'Sachin', 'Megha', 'Rajesh', 'Seema', 'Mohit', 'Alka', 'Prakash', 'Usha',
    'Akash', 'Jyoti', 'Naveen', 'Lata', 'Pankaj', 'Mala', 'Sonu', 'Renu'
]

LAST_NAMES = [
    'Sharma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Shah', 'Mehta', 'Joshi',
    'Reddy', 'Nair', 'Rao', 'Verma', 'Iyer', 'Desai', 'Bhatt', 'Thakur',
    'Agarwal', 'Bansal', 'Malhotra', 'Saxena', 'Sinha', 'Jain', 'Kapoor', 'Chopra',
    'Khanna', 'Bose', 'Pillai', 'Menon', 'Kulkarni', 'Deshpande', 'Patil', 'Pawar'
]

STATUS_MESSAGES = [
    "Hey there! I'm using Vatochito 👋",
    "Busy 📵",
    "At work 💼",
    "Available ✅",
    "Can't talk, WhatsApp only 😊",
    "Sleeping 😴",
    "At the gym 💪",
    "In a meeting 📅",
    "Driving 🚗",
    "Battery about to die 🔋",
    "Happy 😊",
    "Feeling blessed 🙏",
    "Live, laugh, love ❤️",
    "Making memories 📸",
    "Living my best life 🌟",
    "",  # Empty status
]

BIO_TEMPLATES = [
    "Software Engineer | Tech Enthusiast",
    "Traveler 🌍 | Foodie 🍕",
    "Entrepreneur | Startup Founder",
    "Student | Learning new things every day",
    "Designer | Creative Mind",
    "Fitness Freak | Gym Lover 💪",
    "Music Lover 🎵 | Movie Buff 🎬",
    "Photographer 📷 | Nature Lover 🌿",
    "Developer | Open Source Contributor",
    "Digital Marketer | Content Creator",
    "Teacher | Mentor | Guide",
    "Doctor | Helping people heal",
    "Artist | Painting my world 🎨",
    "Writer | Storyteller ✍️",
    "Gamer | Streamer 🎮",
]

def generate_username(first, last, number):
    """Generate unique username"""
    base = f"{first.lower()}.{last.lower()}"
    if number == 0:
        return base
    return f"{base}{number}"

def create_test_users(count=500):
    """Create test users with realistic data"""
    print("=" * 70)
    print(f"Creating {count} Test Users for Vatochito")
    print("=" * 70)
    
    created_count = 0
    existing_count = 0
    
    for i in range(count):
        # Generate name
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        
        # Generate unique username
        username_base = f"{first_name.lower()}.{last_name.lower()}"
        username = username_base if i < 100 else f"{username_base}{i}"
        email = f"{username}@vatochito.com"
        
        # Check if user exists
        if User.objects.filter(username=username).exists():
            existing_count += 1
            continue
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password='test123',  # Same password for all test users
            first_name=first_name,
            last_name=last_name,
            bio=random.choice(BIO_TEMPLATES),
            status_message=random.choice(STATUS_MESSAGES),
            phone_number=f'+91{random.randint(7000000000, 9999999999)}',
            is_online=random.choice([True, False]),
        )
        
        # Create user settings
        UserSettings.objects.create(
            user=user,
            theme=random.choice(['light', 'dark', 'auto']),
            notification_sound=random.choice([True, False]),
            message_preview=random.choice([True, False]),
            show_read_receipts=random.choice([True, False]),
            show_typing_indicator=random.choice([True, False]),
            enable_notifications=random.choice([True, False, True]),  # Mostly True
            auto_download_photos=random.choice([True, False]),
            auto_download_videos=random.choice([True, False]),
        )
        
        created_count += 1
        
        # Progress indicator
        if (i + 1) % 50 == 0:
            print(f"✓ Created {created_count} users... ({i + 1}/{count})")
    
    print("\n" + "=" * 70)
    print("✅ User Generation Complete!")
    print("=" * 70)
    print(f"\nStatistics:")
    print(f"  - Created: {created_count} users")
    print(f"  - Existing: {existing_count} users")
    print(f"  - Total: {User.objects.count()} users in database")
    print(f"\n📝 All users have password: test123")
    print(f"\n💡 Example logins:")
    
    # Show some example users
    sample_users = User.objects.all()[:10]
    for user in sample_users:
        status = "🟢 Online" if user.is_online else "⚫ Offline"
        print(f"  - {user.username} | {user.get_full_name()} | {status}")
    
    print(f"\n🚀 You can now test with 500 concurrent users!")
    print(f"   Each user can login with: username / test123")

def create_sample_conversations():
    """Create some sample conversations between random users"""
    from chat.models import Conversation, ConversationMembership, Message
    
    print("\n" + "=" * 70)
    print("Creating Sample Conversations")
    print("=" * 70)
    
    users = list(User.objects.all()[:100])  # First 100 users
    conversation_count = 0
    
    # Create 50 random conversations
    for i in range(50):
        user1, user2 = random.sample(users, 2)
        
        # Check if conversation already exists
        existing = Conversation.objects.filter(
            conversation_type='direct',
            memberships__user=user1
        ).filter(
            memberships__user=user2
        ).exists()
        
        if existing:
            continue
        
        # Create conversation
        conversation = Conversation.objects.create(
            conversation_type='direct',
            title=f"{user1.username}-{user2.username}"
        )
        
        # Add members
        ConversationMembership.objects.create(
            conversation=conversation,
            user=user1
        )
        ConversationMembership.objects.create(
            conversation=conversation,
            user=user2
        )
        
        # Add some messages
        messages = [
            f"Hey {user2.first_name}! How are you?",
            f"Hi {user1.first_name}! I'm good, thanks!",
            "Great to connect with you on Vatochito!",
            "Yes, this is amazing! 🎉",
        ]
        
        for j, content in enumerate(messages):
            sender = user1 if j % 2 == 0 else user2
            Message.objects.create(
                conversation=conversation,
                sender=sender,
                content=content,
                message_type='text'
            )
        
        conversation_count += 1
    
    print(f"\n✓ Created {conversation_count} conversations")
    print(f"✓ Total conversations: {Conversation.objects.count()}")

if __name__ == '__main__':
    import sys
    
    try:
        # Get count from command line or use default
        count = int(sys.argv[1]) if len(sys.argv) > 1 else 500
        
        print(f"\n🚀 Starting user generation...")
        create_test_users(count)
        
        # Ask if want to create sample conversations
        print(f"\n📊 Creating sample conversations for testing...")
        create_sample_conversations()
        
        print(f"\n✅ Setup Complete! Your WhatsApp-like chat is ready!")
        print(f"   Total Users: {User.objects.count()}")
        print(f"   Total Conversations: {count} (from chat.models import Conversation; Conversation.objects.count())")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
