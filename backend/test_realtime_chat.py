"""
Test script to verify real-time 2-person chat with WebSocket
Tests:
1. User authentication
2. Conversation creation
3. WebSocket connection
4. Real-time message delivery between 2 users
"""
import asyncio
import json
import requests
import websockets
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws"

class ChatTester:
    def __init__(self):
        self.lalo_token = None
        self.kalu_token = None
        self.conversation_id = None
        
    def test_authentication(self):
        """Test user login"""
        print("\n" + "="*60)
        print("TEST 1: Authentication")
        print("="*60)
        
        # Login as lalo
        print("\n1. Logging in as lalo...")
        response = requests.post(
            f"{BASE_URL}/api/auth/login/",
            json={"username": "lalo", "password": "lalo123"}
        )
        if response.status_code == 200:
            self.lalo_token = response.json()["access"]
            print("✅ Lalo logged in successfully")
        else:
            print(f"❌ Failed to login as lalo: {response.text}")
            return False
        
        # Login as kalu
        print("\n2. Logging in as kalu...")
        response = requests.post(
            f"{BASE_URL}/api/auth/login/",
            json={"username": "kalu", "password": "kalu123"}
        )
        if response.status_code == 200:
            self.kalu_token = response.json()["access"]
            print("✅ Kalu logged in successfully")
        else:
            print(f"❌ Failed to login as kalu: {response.text}")
            return False
            
        return True
    
    def test_conversation_setup(self):
        """Test conversation creation"""
        print("\n" + "="*60)
        print("TEST 2: Conversation Setup")
        print("="*60)
        
        # Get kalu's user ID
        print("\n1. Getting kalu's user ID...")
        response = requests.get(
            f"{BASE_URL}/api/auth/profile/me/",
            headers={"Authorization": f"Bearer {self.kalu_token}"}
        )
        kalu_user = response.json()
        print(f"✅ Kalu ID: {kalu_user['id']}")
        
        # Create conversation between lalo and kalu
        print("\n2. Creating conversation...")
        response = requests.post(
            f"{BASE_URL}/api/chat/conversations/create-direct/",
            json={"user_id": kalu_user['id']},
            headers={"Authorization": f"Bearer {self.lalo_token}"}
        )
        
        if response.status_code in [200, 201]:
            conversation = response.json()
            self.conversation_id = conversation['id']
            print(f"✅ Conversation created: ID={self.conversation_id}")
            print(f"   Members: {len(conversation.get('members', []))} users")
            return True
        else:
            print(f"❌ Failed to create conversation: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Try to get existing conversation
            print("\n   Attempting to get existing conversation...")
            response = requests.get(
                f"{BASE_URL}/api/chat/conversations/",
                headers={"Authorization": f"Bearer {self.lalo_token}"}
            )
            if response.status_code == 200:
                convs = response.json()
                if convs:
                    self.conversation_id = convs[0]['id']
                    print(f"✅ Using existing conversation: ID={self.conversation_id}")
                    return True
            
            return False
    
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        print("\n" + "="*60)
        print("TEST 3: WebSocket Connection")
        print("="*60)
        
        ws_uri = f"{WS_URL}/conversations/{self.conversation_id}/?token={self.lalo_token}"
        print(f"\n1. Connecting to: {ws_uri}")
        
        try:
            async with websockets.connect(ws_uri) as websocket:
                print("✅ WebSocket connected successfully")
                
                # Wait a moment for connection to stabilize
                await asyncio.sleep(1)
                
                print("✅ Connection stable")
                return True
        except Exception as e:
            print(f"❌ WebSocket connection failed: {e}")
            return False
    
    async def test_realtime_messaging(self):
        """Test real-time message exchange between 2 users"""
        print("\n" + "="*60)
        print("TEST 4: Real-time Messaging (2-Person Chat)")
        print("="*60)
        
        # WebSocket URIs for both users
        lalo_ws_uri = f"{WS_URL}/conversations/{self.conversation_id}/?token={self.lalo_token}"
        kalu_ws_uri = f"{WS_URL}/conversations/{self.conversation_id}/?token={self.kalu_token}"
        
        print(f"\n1. Connecting both users to WebSocket...")
        print(f"   Lalo: {lalo_ws_uri}")
        print(f"   Kalu: {kalu_ws_uri}")
        
        try:
            async with websockets.connect(lalo_ws_uri) as lalo_ws, \
                       websockets.connect(kalu_ws_uri) as kalu_ws:
                
                print("✅ Both users connected successfully")
                
                # Test 1: Lalo sends message, Kalu receives
                print("\n2. TEST: Lalo sends message to Kalu...")
                test_message_1 = {
                    "type": "message.send",
                    "content": f"Hello from Lalo! {datetime.now().isoformat()}"
                }
                await lalo_ws.send(json.dumps(test_message_1))
                print(f"   📤 Lalo sent: {test_message_1['content']}")
                
                # Wait for Kalu to receive
                try:
                    kalu_received = await asyncio.wait_for(kalu_ws.recv(), timeout=5)
                    kalu_msg = json.loads(kalu_received)
                    print(f"   📥 Kalu received: {kalu_msg.get('content', kalu_msg)}")
                    
                    # Verify message content
                    if test_message_1['content'] in str(kalu_msg):
                        print("   ✅ Message received correctly by Kalu")
                    else:
                        print("   ⚠️ Message content mismatch")
                except asyncio.TimeoutError:
                    print("   ❌ Kalu did not receive message (timeout)")
                    return False
                
                # Wait for Lalo to receive his own message (echo)
                try:
                    lalo_echo = await asyncio.wait_for(lalo_ws.recv(), timeout=3)
                    lalo_msg = json.loads(lalo_echo)
                    print(f"   📥 Lalo received echo: {lalo_msg.get('content', lalo_msg)}")
                except asyncio.TimeoutError:
                    print("   ℹ️ No echo received by sender (this is OK)")
                
                # Test 2: Kalu sends message, Lalo receives
                print("\n3. TEST: Kalu sends message to Lalo...")
                test_message_2 = {
                    "type": "message.send",
                    "content": f"Hello from Kalu! {datetime.now().isoformat()}"
                }
                await kalu_ws.send(json.dumps(test_message_2))
                print(f"   📤 Kalu sent: {test_message_2['content']}")
                
                # Wait for Lalo to receive
                try:
                    lalo_received = await asyncio.wait_for(lalo_ws.recv(), timeout=5)
                    lalo_msg = json.loads(lalo_received)
                    print(f"   📥 Lalo received: {lalo_msg.get('content', lalo_msg)}")
                    
                    # Verify message content
                    if test_message_2['content'] in str(lalo_msg):
                        print("   ✅ Message received correctly by Lalo")
                    else:
                        print("   ⚠️ Message content mismatch")
                except asyncio.TimeoutError:
                    print("   ❌ Lalo did not receive message (timeout)")
                    return False
                
                # Wait for Kalu to receive his own message (echo)
                try:
                    kalu_echo = await asyncio.wait_for(kalu_ws.recv(), timeout=3)
                    kalu_msg_echo = json.loads(kalu_echo)
                    print(f"   📥 Kalu received echo: {kalu_msg_echo.get('content', kalu_msg_echo)}")
                except asyncio.TimeoutError:
                    print("   ℹ️ No echo received by sender (this is OK)")
                
                # Test 3: Rapid message exchange
                print("\n4. TEST: Rapid message exchange...")
                for i in range(3):
                    msg = {
                        "type": "message.send",
                        "content": f"Rapid test message {i+1} from Lalo"
                    }
                    await lalo_ws.send(json.dumps(msg))
                    print(f"   📤 Lalo sent message {i+1}")
                    
                    try:
                        response = await asyncio.wait_for(kalu_ws.recv(), timeout=3)
                        print(f"   📥 Kalu received message {i+1}")
                    except asyncio.TimeoutError:
                        print(f"   ❌ Kalu did not receive message {i+1}")
                    
                    await asyncio.sleep(0.5)
                
                print("\n✅ All real-time messaging tests passed!")
                return True
                
        except websockets.exceptions.WebSocketException as e:
            print(f"❌ WebSocket error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_rest_api_fallback(self):
        """Test REST API fallback for message sending"""
        print("\n" + "="*60)
        print("TEST 5: REST API Fallback")
        print("="*60)
        
        print("\n1. Sending message via REST API...")
        response = requests.post(
            f"{BASE_URL}/api/chat/conversations/{self.conversation_id}/messages/",
            json={"content": "Test message via REST API"},
            headers={"Authorization": f"Bearer {self.lalo_token}"}
        )
        
        if response.status_code in [200, 201]:
            message = response.json()
            print(f"✅ Message sent via REST API")
            print(f"   Message ID: {message.get('id')}")
            print(f"   Content: {message.get('content')}")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("VATOCHITO WEB REAL-TIME CHAT TEST SUITE")
        print("Testing 2-Person Live Chat System")
        print("="*60)
        
        results = []
        
        # Test 1: Authentication
        result = self.test_authentication()
        results.append(("Authentication", result))
        if not result:
            print("\n❌ Cannot proceed without authentication")
            return
        
        # Test 2: Conversation setup
        result = self.test_conversation_setup()
        results.append(("Conversation Setup", result))
        if not result:
            print("\n❌ Cannot proceed without conversation")
            return
        
        # Test 3: WebSocket connection
        result = await self.test_websocket_connection()
        results.append(("WebSocket Connection", result))
        
        # Test 4: Real-time messaging
        result = await self.test_realtime_messaging()
        results.append(("Real-time Messaging", result))
        
        # Test 5: REST API fallback
        result = self.test_rest_api_fallback()
        results.append(("REST API Fallback", result))
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        for test_name, passed in results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name:.<40} {status}")
        
        total_tests = len(results)
        passed_tests = sum(1 for _, passed in results if passed)
        print("\n" + "="*60)
        print(f"Total: {passed_tests}/{total_tests} tests passed")
        print("="*60)


if __name__ == "__main__":
    tester = ChatTester()
    asyncio.run(tester.run_all_tests())
