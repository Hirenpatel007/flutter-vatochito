"""
Create test conversation between two users
Run with: python manage.py shell < create_test_conversation.py
"""
from chat.models import Conversation, ConversationMembership
from accounts.models import User

def create_test_conversation():
    """Create a conversation between lalo and kalu"""
    
    # Get or create users
    try:
        user1 = User.objects.get(username='lalo')
        print(f"✅ Found user: lalo (ID: {user1.id})")
    except User.DoesNotExist:
        user1 = User.objects.create_user(
            username='lalo',
            password='lalo123',
            email='lalo@vatochito.local'
        )
        print(f"✅ Created user: lalo (ID: {user1.id})")
    
    try:
        user2 = User.objects.get(username='kalu')
        print(f"✅ Found user: kalu (ID: {user2.id})")
    except User.DoesNotExist:
        user2 = User.objects.create_user(
            username='kalu',
            password='kalu123',
            email='kalu@vatochito.local'
        )
        print(f"✅ Created user: kalu (ID: {user2.id})")
    
    # Check if conversation already exists
    existing = Conversation.objects.filter(
        memberships__user=user1
    ).filter(
        memberships__user=user2
    ).first()
    
    if existing:
        print(f"⚠️ Conversation already exists: {existing.id}")
        return existing
    
    # Create conversation
    conversation = Conversation.objects.create(
        title=None,  # Direct chat has no title
        owner=user1
    )
    print(f"✅ Created conversation: {conversation.id}")
    
    # Add both users as members
    ConversationMembership.objects.create(
        conversation=conversation,
        user=user1,
        is_admin=True
    )
    print(f"✅ Added {user1.username} to conversation")
    
    ConversationMembership.objects.create(
        conversation=conversation,
        user=user2,
        is_admin=False
    )
    print(f"✅ Added {user2.username} to conversation")
    
    print(f"\n🎉 Success! Conversation ID: {conversation.id}")
    print(f"Users can now chat between lalo and kalu")
    
    return conversation

if __name__ == "__main__":
    create_test_conversation()
