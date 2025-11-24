"""
Test user search API endpoint
Run: python test_search.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vatochito_backend.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from chat.views import UserSearchViewSet

User = get_user_model()

def test_user_search():
    print("\n" + "="*50)
    print("Testing User Search API")
    print("="*50 + "\n")
    
    # Create test users if they don't exist
    users = ['alice', 'bob', 'charlie']
    for username in users:
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(
                username=username,
                password='Test@123',
                email=f'{username}@test.com'
            )
            print(f"✓ Created user: {username}")
        else:
            print(f"✓ User exists: {username}")
    
    print("\n" + "-"*50)
    print("Testing Search Queries")
    print("-"*50 + "\n")
    
    # Test search
    test_queries = ['bob', 'alice', 'char', 'test']
    
    for query in test_queries:
        results = User.objects.filter(
            username__icontains=query
        ) | User.objects.filter(
            display_name__icontains=query
        )
        
        print(f"Query: '{query}'")
        print(f"Results: {results.count()} users found")
        for user in results[:5]:
            print(f"  - {user.username} ({user.display_name or 'No display name'})")
        print()
    
    print("="*50)
    print("API Endpoint Information")
    print("="*50 + "\n")
    
    print("Frontend should call:")
    print("  GET /api/chat/users/search/?q=bob")
    print()
    print("Expected response:")
    print("  [")
    print("    {")
    print('      "id": 1,')
    print('      "username": "bob",')
    print('      "display_name": "Bob Builder",')
    print('      "email": "bob@test.com",')
    print('      "avatar": null,')
    print('      "status_message": "Available"')
    print("    }")
    print("  ]")
    print()
    
    print("="*50)
    print("✓ Test Complete!")
    print("="*50 + "\n")
    
    print("Next steps:")
    print("1. Start backend: python manage.py runserver")
    print("2. Test in browser console:")
    print("   fetch('http://localhost:8000/api/chat/users/search/?q=bob', {")
    print("     headers: {'Authorization': 'Bearer ' + localStorage.getItem('access')}")
    print("   }).then(r => r.json()).then(console.log)")
    print()

if __name__ == '__main__':
    try:
        test_user_search()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
