"""
Mobile API Testing Script for Vatochito
Tests all REST API endpoints to ensure they work properly for mobile apps
"""

import requests
import json
from pprint import pprint

# Configuration
BASE_URL = "http://localhost:8000/api"
WS_URL = "ws://localhost:8000"

class VatochitoMobileAPITester:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.conversation_id = None
        self.message_id = None
        
    def print_response(self, title, response):
        """Pretty print API response"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
        print(f"Status Code: {response.status_code}")
        try:
            data = response.json()
            print("Response:")
            pprint(data, indent=2)
        except:
            print("Response:", response.text)
        print(f"{'='*60}\n")
        
    def get_headers(self, auth=True):
        """Get request headers"""
        headers = {"Content-Type": "application/json"}
        if auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    # 1. AUTHENTICATION TESTS
    
    def test_register(self):
        """Test user registration"""
        url = f"{BASE_URL}/accounts/register/"
        data = {
            "username": "mobile_test_user",
            "email": "mobile@test.com",
            "password": "Test@123",
            "phone_number": "+919876543210",
            "display_name": "Mobile Test User"
        }
        response = requests.post(url, json=data)
        self.print_response("📱 REGISTER USER", response)
        
        if response.status_code == 201:
            result = response.json()
            self.access_token = result.get('access')
            self.refresh_token = result.get('refresh')
            self.user_id = result.get('id')
            return True
        return False
    
    def test_login(self):
        """Test user login"""
        url = f"{BASE_URL}/accounts/login/"
        data = {
            "username": "alice",
            "password": "Test@123"
        }
        response = requests.post(url, json=data)
        self.print_response("🔐 LOGIN", response)
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result.get('access')
            self.refresh_token = result.get('refresh')
            self.user_id = result['user']['id']
            return True
        return False
    
    def test_refresh_token(self):
        """Test token refresh"""
        url = f"{BASE_URL}/accounts/token/refresh/"
        data = {"refresh": self.refresh_token}
        response = requests.post(url, json=data)
        self.print_response("🔄 REFRESH TOKEN", response)
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result.get('access')
            return True
        return False
    
    # 2. PROFILE TESTS
    
    def test_get_profile(self):
        """Test get current user profile"""
        url = f"{BASE_URL}/accounts/profile/me/"
        response = requests.get(url, headers=self.get_headers())
        self.print_response("👤 GET PROFILE", response)
        return response.status_code == 200
    
    def test_update_profile(self):
        """Test update profile"""
        url = f"{BASE_URL}/accounts/profile/me/"
        data = {
            "display_name": "Updated Mobile User",
            "bio": "Testing from mobile",
            "status_message": "Online from mobile app",
            "city": "Mumbai"
        }
        response = requests.patch(url, json=data, headers=self.get_headers())
        self.print_response("✏️ UPDATE PROFILE", response)
        return response.status_code == 200
    
    def test_view_other_profile(self):
        """Test viewing another user's profile"""
        # View Bob's profile (user_id = 2)
        url = f"{BASE_URL}/accounts/profile/2/"
        response = requests.get(url, headers=self.get_headers())
        self.print_response("👀 VIEW OTHER PROFILE", response)
        return response.status_code == 200
    
    # 3. SETTINGS TESTS
    
    def test_get_settings(self):
        """Test get user settings"""
        url = f"{BASE_URL}/accounts/settings/me/"
        response = requests.get(url, headers=self.get_headers())
        self.print_response("⚙️ GET SETTINGS", response)
        return response.status_code == 200
    
    def test_update_settings(self):
        """Test update settings"""
        url = f"{BASE_URL}/accounts/settings/me/"
        data = {
            "notifications_enabled": True,
            "theme": "dark",
            "language": "gu",
            "read_receipts": True
        }
        response = requests.patch(url, json=data, headers=self.get_headers())
        self.print_response("🔧 UPDATE SETTINGS", response)
        return response.status_code == 200
    
    # 4. SEARCH TESTS
    
    def test_search_users(self):
        """Test user search"""
        url = f"{BASE_URL}/chat/users/search/?search=bob"
        response = requests.get(url, headers=self.get_headers())
        self.print_response("🔍 SEARCH USERS", response)
        return response.status_code == 200
    
    # 5. CONVERSATION TESTS
    
    def test_list_conversations(self):
        """Test list conversations"""
        url = f"{BASE_URL}/chat/conversations/"
        response = requests.get(url, headers=self.get_headers())
        self.print_response("💬 LIST CONVERSATIONS", response)
        
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                self.conversation_id = data[0]['id']
            return True
        return False
    
    def test_create_direct_chat(self):
        """Test create direct chat"""
        url = f"{BASE_URL}/chat/conversations/create-direct/"
        data = {"user_id": 2}  # Bob's user_id
        response = requests.post(url, json=data, headers=self.get_headers())
        self.print_response("➕ CREATE DIRECT CHAT", response)
        
        if response.status_code in [200, 201]:
            result = response.json()
            self.conversation_id = result['id']
            return True
        return False
    
    def test_get_conversation_details(self):
        """Test get conversation details"""
        if not self.conversation_id:
            print("⚠️ Skipping - No conversation ID")
            return False
            
        url = f"{BASE_URL}/chat/conversations/{self.conversation_id}/"
        response = requests.get(url, headers=self.get_headers())
        self.print_response("📋 GET CONVERSATION DETAILS", response)
        return response.status_code == 200
    
    # 6. MESSAGE TESTS
    
    def test_list_messages(self):
        """Test list messages in conversation"""
        if not self.conversation_id:
            print("⚠️ Skipping - No conversation ID")
            return False
            
        url = f"{BASE_URL}/chat/conversations/{self.conversation_id}/messages/"
        response = requests.get(url, headers=self.get_headers())
        self.print_response("📨 LIST MESSAGES", response)
        
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                self.message_id = data[0]['id']
            return True
        return False
    
    def test_send_message(self):
        """Test send message"""
        if not self.conversation_id:
            print("⚠️ Skipping - No conversation ID")
            return False
            
        url = f"{BASE_URL}/chat/conversations/{self.conversation_id}/messages/"
        data = {
            "content": "Hello from mobile API test! 📱",
            "message_type": "text"
        }
        response = requests.post(url, json=data, headers=self.get_headers())
        self.print_response("📤 SEND MESSAGE", response)
        
        if response.status_code == 201:
            result = response.json()
            self.message_id = result['id']
            return True
        return False
    
    def test_search_messages(self):
        """Test search messages"""
        if not self.conversation_id:
            print("⚠️ Skipping - No conversation ID")
            return False
            
        url = f"{BASE_URL}/chat/conversations/{self.conversation_id}/messages/?search=hello"
        response = requests.get(url, headers=self.get_headers())
        self.print_response("🔎 SEARCH MESSAGES", response)
        return response.status_code == 200
    
    # 7. CONTACT TESTS
    
    def test_list_contacts(self):
        """Test list contacts"""
        url = f"{BASE_URL}/chat/contacts/"
        response = requests.get(url, headers=self.get_headers())
        self.print_response("📇 LIST CONTACTS", response)
        return response.status_code == 200
    
    # 8. COMPREHENSIVE TEST
    
    def run_all_tests(self):
        """Run all API tests"""
        print("\n" + "="*60)
        print("  🧪 VATOCHITO MOBILE API TESTING")
        print("="*60)
        
        tests = [
            ("Authentication - Login", self.test_login),
            ("Profile - Get", self.test_get_profile),
            ("Profile - Update", self.test_update_profile),
            ("Profile - View Other", self.test_view_other_profile),
            ("Settings - Get", self.test_get_settings),
            ("Settings - Update", self.test_update_settings),
            ("Search - Users", self.test_search_users),
            ("Conversations - List", self.test_list_conversations),
            ("Conversations - Create Direct", self.test_create_direct_chat),
            ("Conversations - Get Details", self.test_get_conversation_details),
            ("Messages - List", self.test_list_messages),
            ("Messages - Send", self.test_send_message),
            ("Messages - Search", self.test_search_messages),
            ("Contacts - List", self.test_list_contacts),
            ("Authentication - Refresh Token", self.test_refresh_token),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                status = "✅ PASS" if result else "❌ FAIL"
                results.append((test_name, status))
            except Exception as e:
                results.append((test_name, f"❌ ERROR: {str(e)}"))
        
        # Print summary
        print("\n" + "="*60)
        print("  📊 TEST SUMMARY")
        print("="*60)
        for test_name, status in results:
            print(f"{status:12} | {test_name}")
        
        passed = sum(1 for _, status in results if "✅" in status)
        total = len(results)
        print("="*60)
        print(f"  Results: {passed}/{total} tests passed ({int(passed/total*100)}%)")
        print("="*60 + "\n")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         VATOCHITO MOBILE API TESTING SCRIPT              ║
    ║                                                          ║
    ║  This script tests all REST API endpoints for mobile    ║
    ║  app integration.                                        ║
    ║                                                          ║
    ║  Prerequisites:                                          ║
    ║  1. Backend server running on port 8000                 ║
    ║  2. Test user 'alice' exists with password 'Test@123'   ║
    ║  3. Test user 'bob' exists (user_id = 2)                ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    tester = VatochitoMobileAPITester()
    tester.run_all_tests()
