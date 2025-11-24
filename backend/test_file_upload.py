#!/usr/bin/env python
"""
Test file upload functionality
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vatochito_backend.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from chat.models import Conversation, Message, Attachment
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image

User = get_user_model()

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return ContentFile(buffer.read(), 'test_image.jpg')

def test_file_upload():
    print("=" * 60)
    print("Testing File Upload Functionality")
    print("=" * 60)
    
    # Get test users
    alice = User.objects.filter(username='alice').first()
    bob = User.objects.filter(username='bob').first()
    
    if not alice or not bob:
        print("❌ Test users not found. Run setup_test_chat.py first.")
        return
    
    print(f"✓ Found users: {alice.username}, {bob.username}")
    
    # Get or create conversation
    conversation = Conversation.objects.filter(
        conversation_type='direct',
        memberships__user__in=[alice, bob]
    ).distinct().first()
    
    if not conversation:
        print("❌ No conversation found. Create one first.")
        return
    
    print(f"✓ Using conversation: {conversation.id}")
    
    # Create test message with image attachment
    print("\n📤 Creating message with image attachment...")
    
    message = Message.objects.create(
        conversation=conversation,
        sender=alice,
        message_type='image',
        content='Test image upload'
    )
    
    # Create attachment
    test_image = create_test_image()
    attachment = Attachment.objects.create(
        message=message,
        file=test_image,
        file_name='test_image.jpg',
        file_size=test_image.size,
        mime_type='image/jpeg'
    )
    
    print(f"✓ Message created: ID {message.id}")
    print(f"✓ Attachment created: ID {attachment.id}")
    print(f"  - File: {attachment.file.name}")
    print(f"  - Size: {attachment.file_size} bytes")
    print(f"  - MIME: {attachment.mime_type}")
    
    # Verify attachment
    print("\n🔍 Verifying attachment...")
    retrieved_message = Message.objects.get(id=message.id)
    attachments = retrieved_message.attachments.all()
    
    if attachments.count() == 1:
        print(f"✓ Attachment verified: {attachments[0].file_name}")
        print(f"  - URL: {attachments[0].file.url}")
    else:
        print(f"❌ Attachment count mismatch: {attachments.count()}")
        return
    
    # Test file access
    print("\n📂 Testing file access...")
    try:
        file_path = attachment.file.path
        if os.path.exists(file_path):
            print(f"✓ File exists: {file_path}")
            print(f"  - Size on disk: {os.path.getsize(file_path)} bytes")
        else:
            print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"⚠️  File check error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ File Upload Test Complete!")
    print("=" * 60)
    print(f"\nTest Results:")
    print(f"  - Message ID: {message.id}")
    print(f"  - Attachment ID: {attachment.id}")
    print(f"  - File Type: {attachment.mime_type}")
    print(f"  - File Name: {attachment.file_name}")
    print(f"\n💡 You can now test in the frontend by:")
    print(f"  1. Open chat with {bob.username}")
    print(f"  2. Click attachment button (📎)")
    print(f"  3. Select an image, video, or document")
    print(f"  4. Click send")

if __name__ == '__main__':
    try:
        test_file_upload()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
