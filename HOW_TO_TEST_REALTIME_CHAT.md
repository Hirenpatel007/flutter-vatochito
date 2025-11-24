# How to Test Real-Time Chat on Web

## Quick Start Guide

### Prerequisites
- Python 3.10+ installed
- Flutter SDK installed
- Backend dependencies installed (`pip install -r backend/requirements.txt`)

---

## Step 1: Start Backend with WebSocket Support

**IMPORTANT**: You MUST use Daphne (ASGI server), NOT `runserver`!

```bash
cd backend
py -m daphne -b 127.0.0.1 -p 8000 vatochito_backend.asgi:application
```

✅ **You should see**:
```
INFO     Starting server at tcp:port=8000:interface=127.0.0.1
INFO     Listening on TCP address 127.0.0.1:8000
```

❌ **DON'T use this** (no WebSocket support):
```bash
python manage.py runserver  # ❌ This won't work for WebSockets!
```

---

## Step 2: Start Flutter Web App

### Option A: Development Mode (Hot Reload)
```bash
flutter run -d chrome --web-port 5173
```

### Option B: Production Build
```bash
flutter build web
cd build/web
python -m http.server 5173
```

Then open: `http://localhost:5173`

---

## Step 3: Test 2-Person Real-Time Chat

### Test Scenario: Two Users Chatting

1. **Open TWO browser windows/tabs** (or two different browsers)

2. **Window 1 - User: Lalo**
   - Go to: `http://localhost:5173`
   - Click "Login"
   - Username: `lalo`
   - Password: `lalo123`
   - Click "Submit"
   - Navigate to conversations
   - Open conversation with Kalu

3. **Window 2 - User: Kalu** (in another window/tab)
   - Go to: `http://localhost:5173`
   - Click "Login"
   - Username: `kalu`
   - Password: `kalu123`
   - Click "Submit"
   - Navigate to conversations
   - Open conversation with Lalo

4. **Send Messages**
   - In Window 1 (Lalo): Type "Hello from Lalo!" and press Send
   - **Watch Window 2** → Message should appear INSTANTLY! 🚀
   - In Window 2 (Kalu): Type "Hi Lalo, I got your message!" and press Send
   - **Watch Window 1** → Message should appear INSTANTLY! 🚀

5. **Rapid Fire Test**
   - Send multiple messages back and forth quickly
   - All messages should appear in real-time on both sides
   - No lag, no duplicates

---

## Step 4: Verify WebSocket Connection

### Check Browser Developer Tools

1. **Open DevTools** (F12 or Right-click → Inspect)

2. **Go to Console tab**

✅ **Look for these logs**:
```
🔌 Connecting to WebSocket for conversation: 1
🔌 Connecting to WebSocket: ws://127.0.0.1:8000/ws/conversations/1/?token=...
✅ WebSocket channel created
✅ WebSocket connected successfully
```

3. **When you send a message**:
```
📤 Sending WebSocket message: {"type":"message.send","content":"Hello!"}
✉️ Message sent via WebSocket: Hello!
```

4. **When you receive a message**:
```
📨 WebSocket message received: {id: 123, content: "Hello!", sender: {...}, ...}
✅ Message added to chat: Hello!
```

### Check Network Tab

1. **Go to Network tab**
2. **Filter**: WS (WebSocket)
3. **Look for**: `ws://127.0.0.1:8000/ws/conversations/1/`
4. **Status**: Should show `101 Switching Protocols` (connection established)
5. **Messages tab**: You should see JSON messages being sent/received

---

## Step 5: Automated Test (Optional)

### Run Comprehensive Test Script

```bash
# Ensure Daphne is running first!
py backend\test_realtime_chat.py
```

✅ **Expected Output**:
```
============================================================
VATOCHITO WEB REAL-TIME CHAT TEST SUITE
Testing 2-Person Live Chat System
============================================================

TEST 1: Authentication.......................... ✅ PASSED
TEST 2: Conversation Setup...................... ✅ PASSED
TEST 3: WebSocket Connection.................... ✅ PASSED
TEST 4: Real-time Messaging..................... ✅ PASSED
TEST 5: REST API Fallback....................... ✅ PASSED

Total: 5/5 tests passed
```

---

## Troubleshooting

### Problem: "WebSocket 404 Not Found"

❌ **Cause**: Using `runserver` instead of Daphne

✅ **Solution**:
```bash
# Stop runserver
# Start with Daphne:
cd backend
py -m daphne -b 127.0.0.1 -p 8000 vatochito_backend.asgi:application
```

---

### Problem: "Connection Refused"

❌ **Cause**: Backend not running

✅ **Solution**: Start Daphne server (see Step 1)

---

### Problem: "Messages not appearing in real-time"

❌ **Possible Causes**:
1. WebSocket not connected
2. Using `runserver` instead of Daphne
3. Browser blocking WebSocket

✅ **Solutions**:
1. Check DevTools console for WebSocket connection logs
2. Restart with Daphne
3. Try a different browser
4. Check if port 8000 is accessible

---

### Problem: "Duplicate messages appearing"

✅ **Already handled**: The code includes duplicate prevention
```dart
// Check if message already exists to avoid duplicates
final exists = state.messages.any((m) => m.id == message.id);
if (!exists) {
  // Add message
}
```

---

### Problem: "401 Unauthorized on WebSocket"

❌ **Cause**: JWT token expired or invalid

✅ **Solution**:
1. Logout and login again
2. Check token is being sent in WebSocket URL
3. Verify token in DevTools → Network → WS → Headers

---

## Advanced Testing

### Test with Network Throttling

1. Open DevTools → Network tab
2. Set throttling to "Slow 3G"
3. Send messages
4. Verify real-time delivery still works (may be slower)

### Test with Multiple Conversations

1. Create multiple conversations
2. Open different conversation in each window
3. Verify messages only appear in correct conversation

### Test Reconnection

1. Stop Daphne server
2. Send a message (should fail)
3. Start Daphne server again
4. Refresh page
5. Send message (should work)

---

## Performance Benchmarks

### Expected Performance:

| Metric | Value |
|--------|-------|
| Message Delivery Time (local) | < 50ms |
| Connection Establishment | < 500ms |
| Messages per second | 100+ |
| Concurrent users per server | 1000+ |

### How to Measure:

1. Open DevTools → Console
2. Send message
3. Look at timestamp in logs
4. Calculate time difference

---

## What to Look For

### ✅ **SUCCESS INDICATORS**:
- Messages appear instantly on both sides
- WebSocket connected successfully (console logs)
- No 404 or connection errors
- Smooth, real-time communication
- No duplicate messages
- Messages persist after refresh

### ❌ **FAILURE INDICATORS**:
- Messages delayed or not appearing
- WebSocket 404 errors
- Connection refused errors
- Have to refresh to see messages
- Multiple copies of same message

---

## Demo Video Script

### Record a demo showing:

1. **Split Screen**: Two browser windows side by side
2. **Login**: Both users login
3. **Navigate**: Both open same conversation
4. **Chat**:
   - User 1 types and sends → appears instantly in User 2's window
   - User 2 replies → appears instantly in User 1's window
   - Show rapid back-and-forth messaging
5. **DevTools**: Show WebSocket connection status
6. **Network**: Show WebSocket messages in Network tab

---

## Production Deployment Notes

### For Production (Important!):

1. **Use WSS (Secure WebSocket)** for HTTPS sites:
   ```dart
   static const websocketBaseUrl = 'wss://your-domain.com/ws';
   ```

2. **Use Redis** for multi-server support:
   ```python
   CHANNEL_LAYERS = {
       "default": {
           "BACKEND": "channels_redis.core.RedisChannelLayer",
           "CONFIG": {
               "hosts": [("redis", 6379)],
           },
       }
   }
   ```

3. **Configure WebSocket Proxy** (nginx example):
   ```nginx
   location /ws/ {
       proxy_pass http://backend;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
   }
   ```

---

## Summary

### To test 2-person real-time chat:

1. ✅ Start Daphne (not runserver!)
2. ✅ Start Flutter web app
3. ✅ Open two browser windows
4. ✅ Login as two different users
5. ✅ Open same conversation
6. ✅ Send messages back and forth
7. ✅ Watch messages appear INSTANTLY! 🚀

**Expected Result**: Messages should appear in real-time on both sides with < 50ms latency on local network.

---

**Questions?** Check the full test report: `WEB_REALTIME_CHAT_TEST_REPORT.md`
