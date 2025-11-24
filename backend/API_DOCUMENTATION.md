# Vatochito REST API Documentation

## Base URL
- **Development**: `http://localhost:8000/api`
- **Production**: `https://your-domain.com/api`

## Authentication
All endpoints (except registration and login) require JWT authentication.

### Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## 1. Authentication Endpoints

### Register
**POST** `/accounts/register/`

**Request Body:**
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "Test@123",
  "phone_number": "+919876543210",
  "display_name": "Alice"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "display_name": "Alice",
  "phone_number": "+919876543210",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Login
**POST** `/accounts/login/`

**Request Body:**
```json
{
  "username": "alice",
  "password": "Test@123"
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "display_name": "Alice",
    "avatar": "http://localhost:8000/media/avatars/alice.jpg",
    "status_message": "Hey there!",
    "bio": "Software Developer"
  }
}
```

### Refresh Token
**POST** `/accounts/token/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Logout
**POST** `/accounts/logout/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `205 Reset Content`

---

## 2. User Profile Endpoints

### Get Current User Profile
**GET** `/accounts/profile/me/`

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "display_name": "Alice",
  "avatar": "http://localhost:8000/media/avatars/alice.jpg",
  "phone_number": "+919876543210",
  "status_message": "Hey there!",
  "bio": "Software Developer",
  "date_of_birth": "1995-05-15",
  "country": "India",
  "city": "Mumbai",
  "website": "https://alice.dev",
  "show_email": true,
  "show_phone": true,
  "show_online_status": true,
  "show_profile_photo": true,
  "show_about": true
}
```

### Update Profile
**PATCH** `/accounts/profile/me/`

**Request Body:**
```json
{
  "display_name": "Alice Kumar",
  "bio": "Full Stack Developer",
  "status_message": "Building something amazing!",
  "city": "Bangalore"
}
```

**Response:** `200 OK` (returns updated profile)

### Upload Avatar
**POST** `/accounts/profile/upload-avatar/`

**Request:** `multipart/form-data`
```
avatar: <file>
```

**Response:** `200 OK`
```json
{
  "avatar": "http://localhost:8000/media/avatars/alice_abc123.jpg",
  "message": "Avatar uploaded successfully"
}
```

### Delete Avatar
**DELETE** `/accounts/profile/delete-avatar/`

**Response:** `200 OK`
```json
{
  "message": "Avatar deleted successfully"
}
```

### View Other User's Profile
**GET** `/accounts/profile/{user_id}/`

**Response:** `200 OK` (returns public profile based on privacy settings)

---

## 3. Settings Endpoints

### Get Settings
**GET** `/accounts/settings/me/`

**Response:** `200 OK`
```json
{
  "id": 1,
  "notifications_enabled": true,
  "message_notifications": true,
  "group_notifications": true,
  "call_notifications": true,
  "show_online_status": true,
  "show_last_seen": true,
  "read_receipts": true,
  "typing_indicators": true,
  "profile_photo_visibility": "everyone",
  "last_seen_visibility": "contacts",
  "about_visibility": "everyone",
  "two_factor_enabled": false,
  "theme": "light",
  "language": "en",
  "font_size": "medium"
}
```

### Update Settings
**PATCH** `/accounts/settings/me/`

**Request Body:**
```json
{
  "notifications_enabled": false,
  "theme": "dark",
  "language": "gu"
}
```

**Response:** `200 OK` (returns updated settings)

### Reset Settings to Default
**POST** `/accounts/settings/reset/`

**Response:** `200 OK`
```json
{
  "message": "Settings reset to defaults"
}
```

---

## 4. Chat/Conversation Endpoints

### List Conversations
**GET** `/chat/conversations/`

**Query Parameters:**
- `search` (optional): Search by title

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "alice - bob",
    "conversation_type": "direct",
    "owner": 1,
    "description": null,
    "created_at": "2025-11-03T10:30:00Z",
    "updated_at": "2025-11-03T12:45:00Z",
    "avatar": null,
    "is_public": false,
    "invite_link": null,
    "members": [
      {
        "id": 1,
        "user": {
          "id": 1,
          "username": "alice",
          "display_name": "Alice",
          "avatar": "http://localhost:8000/media/avatars/alice.jpg"
        },
        "nickname": null,
        "is_admin": true,
        "joined_at": "2025-11-03T10:30:00Z"
      },
      {
        "id": 2,
        "user": {
          "id": 2,
          "username": "bob",
          "display_name": "Bob",
          "avatar": null
        },
        "nickname": null,
        "is_admin": false,
        "joined_at": "2025-11-03T10:30:00Z"
      }
    ],
    "last_message": {
      "id": 5,
      "content": "Hello Bob!",
      "sender": {
        "id": 1,
        "username": "alice"
      },
      "created_at": "2025-11-03T12:45:00Z"
    },
    "unread_count": 2
  }
]
```

### Create Direct Chat
**POST** `/chat/conversations/create-direct/`

**Request Body:**
```json
{
  "user_id": 2
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "title": "alice - bob",
  "conversation_type": "direct",
  "members": [...],
  "created_at": "2025-11-03T10:30:00Z"
}
```

### Create Group Chat
**POST** `/chat/conversations/`

**Request Body:**
```json
{
  "title": "Dev Team",
  "conversation_type": "group",
  "description": "Team discussion group",
  "member_ids": [2, 3, 4]
}
```

**Response:** `201 Created`

### Get Conversation Details
**GET** `/chat/conversations/{conversation_id}/`

**Response:** `200 OK` (returns full conversation details)

### Add Member to Conversation
**POST** `/chat/conversations/{conversation_id}/add-member/`

**Request Body:**
```json
{
  "user_id": 5
}
```

**Response:** `200 OK`

### Leave Conversation
**POST** `/chat/conversations/{conversation_id}/leave/`

**Response:** `200 OK`

---

## 5. Message Endpoints

### List Messages in Conversation
**GET** `/chat/conversations/{conversation_id}/messages/`

**Query Parameters:**
- `search` (optional): Search message content
- `limit` (optional): Number of messages (default: 50)
- `offset` (optional): Pagination offset

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "conversation": 1,
    "sender": {
      "id": 1,
      "username": "alice",
      "display_name": "Alice",
      "avatar": "http://localhost:8000/media/avatars/alice.jpg"
    },
    "message_type": "text",
    "content": "Hello Bob!",
    "created_at": "2025-11-03T12:45:00Z",
    "edited_at": null,
    "reply_to": null,
    "reply_to_message": null,
    "forwarded_from": null,
    "forwarded_from_message": null,
    "is_deleted": false,
    "attachments": [],
    "receipts": [
      {
        "user": {
          "id": 2,
          "username": "bob"
        },
        "state": "read",
        "updated_at": "2025-11-03T12:46:00Z"
      }
    ],
    "reactions": []
  }
]
```

### Send Message
**POST** `/chat/conversations/{conversation_id}/messages/`

**Request Body:**
```json
{
  "content": "Hello Bob!",
  "message_type": "text",
  "reply_to": null
}
```

**Response:** `201 Created` (returns created message)

### Edit Message
**PATCH** `/chat/conversations/{conversation_id}/messages/{message_id}/edit/`

**Request Body:**
```json
{
  "content": "Hello Bob! How are you?"
}
```

**Response:** `200 OK`

### Delete Message
**DELETE** `/chat/conversations/{conversation_id}/messages/{message_id}/delete/`

**Response:** `204 No Content`

### React to Message
**POST** `/chat/conversations/{conversation_id}/messages/{message_id}/react/`

**Request Body:**
```json
{
  "emoji": "👍"
}
```

**Response:** `200 OK`

### Forward Message
**POST** `/chat/conversations/{conversation_id}/messages/{message_id}/forward/`

**Request Body:**
```json
{
  "target_conversation_id": 2
}
```

**Response:** `201 Created`

---

## 6. User Search Endpoint

### Search Users
**GET** `/chat/users/search/`

**Query Parameters:**
- `search` (required): Search query (username, display_name, phone_number)

**Response:** `200 OK`
```json
[
  {
    "id": 2,
    "username": "bob",
    "display_name": "Bob",
    "avatar": null,
    "status_message": "Available"
  }
]
```

---

## 7. Contact Endpoints

### List Contacts
**GET** `/chat/contacts/`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "contact": {
      "id": 2,
      "username": "bob",
      "display_name": "Bob",
      "avatar": null
    },
    "nickname": "Bobby",
    "is_blocked": false,
    "is_favorite": true,
    "added_at": "2025-11-01T10:00:00Z"
  }
]
```

### Add Contact
**POST** `/chat/contacts/`

**Request Body:**
```json
{
  "contact": 2,
  "nickname": "Bobby"
}
```

**Response:** `201 Created`

### Update Contact
**PATCH** `/chat/contacts/{contact_id}/`

**Request Body:**
```json
{
  "nickname": "Bob Kumar",
  "is_favorite": true
}
```

**Response:** `200 OK`

### Block/Unblock Contact
**POST** `/chat/contacts/{contact_id}/block/`

**Response:** `200 OK`

---

## 8. WebSocket Connection

### Connect to Conversation
**WebSocket URL:** `ws://localhost:8000/ws/chat/{conversation_id}/?token={access_token}`

### Send Message
```json
{
  "type": "message.send",
  "content": "Hello!",
  "message_type": "text",
  "reply_to": null
}
```

### Receive Message
```json
{
  "type": "message.new",
  "data": {
    "id": 1,
    "content": "Hello!",
    "sender": {...},
    "created_at": "2025-11-03T12:45:00Z"
  }
}
```

### Send Typing Indicator
```json
{
  "type": "typing",
  "is_typing": true
}
```

### Receive Typing Indicator
```json
{
  "type": "typing",
  "user_id": 2,
  "username": "bob",
  "is_typing": true
}
```

### Mark Message as Read
```json
{
  "type": "message.read",
  "message_id": 1
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error occurred"
}
```

---

## Mobile App Integration Notes

1. **Store Tokens Securely**: Use secure storage (Keychain on iOS, Keystore on Android) for JWT tokens
2. **Token Refresh**: Implement automatic token refresh when access token expires
3. **WebSocket Reconnection**: Handle network disconnections and reconnect automatically
4. **Offline Support**: Cache messages locally and sync when online
5. **Push Notifications**: Integrate with FCM (Firebase Cloud Messaging) for notifications
6. **Image Optimization**: Compress images before uploading
7. **Pagination**: Implement infinite scroll for message loading
8. **Network Errors**: Handle network errors gracefully with retry logic

---

## Testing the API

See `test_mobile_api.py` for comprehensive API testing examples.
