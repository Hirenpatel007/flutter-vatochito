# Vatochito - Real-time Chat Application

A modern, full-stack real-time chat application built with Flutter and Django, featuring WebSocket-based messaging, user authentication, and media sharing capabilities.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Flutter](https://img.shields.io/badge/Flutter-3.x-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0.9-green.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Deployment](#-deployment)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Project Structure](#-project-structure)

## ✨ Features

### Core Functionality
- 🔐 **User Authentication** - JWT-based authentication with secure token management
- 💬 **Real-time Chat** - WebSocket-powered instant messaging
- 👥 **User Search** - Find and connect with other users
- 📝 **Message Management** - Edit and delete sent messages with real-time updates
- 🖼️ **Profile Management** - Avatar upload, update, and deletion
- 📱 **Mobile-First Design** - Optimized for Android devices
- 🔄 **Message Synchronization** - Real-time updates across all connected clients

### Technical Features
- **WebSocket Support** - Persistent connections for instant message delivery
- **JWT Authentication** - Secure token-based authentication with refresh tokens
- **PostgreSQL Database** - Robust relational data storage
- **Redis Channel Layers** - Scalable WebSocket communication
- **REST API** - Comprehensive RESTful API for mobile integration
- **Image Processing** - Avatar upload and optimization with Pillow
- **BLoC Pattern** - Predictable state management

## 🛠️ Tech Stack

### Frontend
- **Flutter 3.x** - Cross-platform mobile framework
- **BLoC Pattern** - State management with flutter_bloc
- **WebSocket Client** - Real-time communication with web_socket_channel
- **Dio** - HTTP client for API calls
- **Flutter Secure Storage** - Secure token storage
- **Cached Network Image** - Optimized image loading

### Backend
- **Django 5.0.9** - High-level Python web framework
- **Django REST Framework 3.15.2** - Powerful API development
- **Django Channels 4.1.0** - WebSocket and async support
- **Daphne 4.1.2** - ASGI HTTP/WebSocket server
- **PostgreSQL** - Primary relational database
- **Redis 5.0.8** - Channel layer backend for WebSockets
- **JWT Authentication** - djangorestframework-simplejwt 5.3.1
- **Pillow 10.4.0** - Image processing library

### DevOps & Tools
- **Docker** - Container orchestration
- **Render** - Cloud deployment platform
- **Whitenoise 6.7.0** - Static file serving
- **CORS Headers** - Cross-origin resource sharing
- **drf-spectacular** - OpenAPI 3.0 schema generation

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│      Flutter Mobile App         │
│   (BLoC State Management)       │
└────────┬──────────────┬─────────┘
         │              │
         │ REST API     │ WebSocket
         │ (HTTP)       │ (WS/WSS)
         │              │
┌────────▼──────────────▼─────────┐
│     Django Backend               │
│  ┌──────────┐  ┌──────────┐    │
│  │   DRF    │  │ Channels │    │
│  │   API    │  │ Consumer │    │
│  └──────────┘  └──────────┘    │
│  ┌──────────────────────────┐  │
│  │   Daphne ASGI Server     │  │
│  └──────────────────────────┘  │
└────────┬──────────────┬─────────┘
         │              │
    ┌────▼────┐    ┌────▼────┐
    │  Redis  │    │  Postgre│
    │ Channel │    │   SQL   │
    │  Layer  │    │   DB    │
    └─────────┘    └─────────┘
```

## 📦 Prerequisites

### Frontend Development
- **Flutter SDK** 3.0 or higher
- **Dart SDK** 3.0 or higher
- **Android Studio** or **VS Code** with Flutter extensions
- **Java JDK 11** (for Android builds)
- **Android SDK** (API level 21+)

### Backend Development
- **Python 3.11+**
- **PostgreSQL 14+**
- **Redis 7.0+**
- **pip** (Python package manager)
- **virtualenv** or **venv**

## 🚀 Installation

### Backend Setup

1. **Navigate to backend directory**
```cmd
cd c:\flutterhari\project\vatochito\backend
```

2. **Create virtual environment**
```cmd
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```cmd
pip install -r requirements.txt
```

4. **Configure environment variables**
Create `.env` file in `backend/` directory:
```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
DJANGO_SETTINGS_MODULE=vatochito_backend.settings.development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/vatochito_db

# Redis (for WebSocket channels)
REDIS_URL=redis://localhost:6379/0

# CORS
ALLOWED_HOSTS=localhost,127.0.0.1,10.0.2.2
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:8000

# JWT Settings
ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=1440
```

5. **Run database migrations**
```cmd
python manage.py migrate
```

6. **Create superuser (admin)**
```cmd
python manage.py createsuperuser
```

7. **Create test users (optional)**
```cmd
python create_test_users.py
```

### Frontend Setup

1. **Navigate to project root**
```cmd
cd c:\flutterhari\project\vatochito
```

2. **Install Flutter dependencies**
```cmd
flutter pub get
```

3. **Generate code (if needed)**
```cmd
dart run build_runner build --delete-conflicting-outputs
```

4. **Configure API endpoints**
Edit `lib/src/core/constants/app_endpoints.dart`:
- **Development**: `http://10.0.2.2:8000` (Android emulator points to host machine)
- **Production**: Your deployed backend URL (e.g., `https://vatochito-api.onrender.com`)

## ⚙️ Configuration

### Backend Configuration Files

**Settings Structure:**
```
backend/vatochito_backend/settings/
├── base.py           # Shared settings
├── development.py    # Local development
└── production.py     # Production deployment
```

**Development Settings** (`development.py`):
- SQLite database (simple setup)
- In-memory channel layer (no Redis required)
- Debug mode enabled
- Local file storage

**Production Settings** (`production.py`):
- PostgreSQL database
- Redis channel layer (required for WebSockets)
- Security middleware enabled
- HTTPS enforcement
- Whitenoise for static files

### Frontend Configuration

**API Endpoint Switching:**
The app automatically switches between development and production URLs:
```dart
// Automatically uses production URL when built with --release
final String baseUrl = bool.fromEnvironment('dart.vm.product')
    ? 'https://vatochito-api.onrender.com'  // Production
    : 'http://10.0.2.2:8000';                // Development
```

## 🏃 Running the Application

### Start Backend (Development)

**Option 1: Django Development Server**
```cmd
cd backend
python manage.py runserver
```

**Option 2: Daphne ASGI Server (Recommended for WebSockets)**
```cmd
cd backend
daphne -b 0.0.0.0 -p 8000 vatochito_backend.asgi:application
```

**With Redis (for production-like testing):**
1. Start Redis server:
```cmd
redis-server
```

2. Use production settings:
```cmd
set DJANGO_SETTINGS_MODULE=vatochito_backend.settings.production
python manage.py runserver
```

### Start Frontend

**Run on Android Emulator:**
```cmd
flutter run
```

**Run on Physical Android Device:**
```cmd
flutter run --release
```

**Build APK for Distribution:**
```cmd
flutter build apk --release
```
Output: `build\app\outputs\flutter-apk\app-release.apk`

**Build App Bundle (for Google Play):**
```cmd
flutter build appbundle --release
```

## 📁 Project Structure

```
vatochito/
├── android/                   # Android native code & build config
│   ├── app/
│   │   ├── build.gradle.kts  # Android app configuration
│   │   └── src/              # Android source files
│   └── build.gradle.kts      # Android project build config
│
├── assets/                    # App assets
│   ├── icons/                # App icons
│   └── images/               # Images and graphics
│
├── backend/                   # Django Backend
│   ├── accounts/             # User authentication & profiles
│   │   ├── models.py         # Custom User model
│   │   ├── views.py          # Auth API endpoints
│   │   ├── serializers.py    # User serializers
│   │   └── auth_backends.py  # Custom authentication
│   │
│   ├── chat/                 # Chat functionality
│   │   ├── models.py         # Conversation, Message, Attachment models
│   │   ├── views.py          # Chat REST API endpoints
│   │   ├── consumers.py      # WebSocket consumer for real-time
│   │   ├── serializers.py    # Chat serializers
│   │   ├── routing.py        # WebSocket URL routing
│   │   └── middleware.py     # WebSocket authentication
│   │
│   ├── core/                 # Core utilities
│   │   ├── storage.py        # File storage configuration
│   │   └── utils.py          # Helper functions
│   │
│   ├── vatochito_backend/    # Project settings
│   │   ├── settings/
│   │   │   ├── base.py       # Common settings
│   │   │   ├── development.py # Dev environment
│   │   │   └── production.py  # Production environment
│   │   ├── urls.py           # Main URL configuration
│   │   ├── asgi.py           # ASGI config for WebSockets
│   │   └── wsgi.py           # WSGI config for HTTP
│   │
│   ├── media/                # User uploaded files
│   ├── static/               # Static files (CSS, JS)
│   ├── staticfiles/          # Collected static files
│   ├── requirements.txt      # Python dependencies
│   └── manage.py             # Django management script
│
├── lib/                      # Flutter Frontend
│   ├── main.dart            # App entry point
│   └── src/
│       ├── core/            # Core utilities
│       │   └── constants/
│       │       └── app_endpoints.dart  # API URLs
│       │
│       └── features/        # Feature modules
│           ├── auth/        # Authentication feature
│           │   ├── data/
│           │   │   ├── models/
│           │   │   │   └── user_model.dart
│           │   │   └── repositories/
│           │   │       └── auth_repository.dart
│           │   └── presentation/
│           │       ├── bloc/
│           │       │   ├── auth_bloc.dart
│           │       │   └── auth_state.dart
│           │       └── pages/
│           │           ├── login_screen.dart
│           │           └── register_screen.dart
│           │
│           └── chat/        # Chat feature
│               ├── data/
│               │   ├── models/
│               │   │   ├── conversation_model.dart
│               │   │   └── message_model.dart
│               │   └── repositories/
│               │       └── chat_repository.dart
│               └── presentation/
│                   ├── bloc/
│                   │   ├── chat_room_cubit.dart
│                   │   └── conversations_cubit.dart
│                   ├── pages/
│                   │   ├── chat_list_screen.dart
│                   │   └── chat_room_screen.dart
│                   └── widgets/
│                       ├── message_bubble.dart
│                       └── chat_input.dart
│
├── web/                      # Web platform files
│   ├── index.html
│   └── manifest.json
│
├── pubspec.yaml             # Flutter dependencies
├── analysis_options.yaml    # Dart linter rules
└── README.md               # This file
```

## 🌐 Deployment

### Backend Deployment on Render

Render provides free hosting with PostgreSQL and Redis support, perfect for this application.

#### Prerequisites
- GitHub account with repository
- Render account ([render.com](https://render.com))

#### Step 1: Prepare Backend for Deployment

**Environment Variables Required:**
```env
DJANGO_SETTINGS_MODULE=vatochito_backend.settings.production
SECRET_KEY=<generate-strong-random-key>
DEBUG=False
DATABASE_URL=<provided-by-render-postgres>
REDIS_URL=<provided-by-render-redis>
ALLOWED_HOSTS=.onrender.com
CORS_ALLOWED_ORIGINS=https://your-frontend-url.com
```

#### Step 2: Create Render Services

**A. Create PostgreSQL Database:**
1. Go to Render Dashboard
2. Click "New +" → "PostgreSQL"
3. Name: `vatochito-db`
4. Region: Choose nearest to your users
5. Plan: Free
6. Copy the "Internal Database URL" after creation

**B. Create Redis Service:**
1. Click "New +" → "Redis"
2. Name: `vatochito-redis`
3. Region: Same as database
4. Plan: Free (30MB)
5. Copy the "Internal Redis URL" after creation

**C. Create Web Service:**
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `vatochito-api`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**:
   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```
   - **Start Command**:
   ```bash
   daphne -b 0.0.0.0 -p $PORT vatochito_backend.asgi:application
   ```

4. Add Environment Variables (from above list)
5. Click "Create Web Service"

#### Step 3: Verify Deployment

After deployment completes:
1. Check logs for errors
2. Visit `https://your-service.onrender.com/api/` to verify API is running
3. Test WebSocket: `wss://your-service.onrender.com/ws/chat/1/?token=<test-token>`

### Frontend Deployment

#### Option 1: APK Distribution (Recommended for Testing)

**Build release APK:**
```cmd
flutter build apk --release
```

**Distribute:**
- Direct download from website
- Email to testers
- Firebase App Distribution
- APKPure / APKMirror (for wider distribution)

#### Option 2: Google Play Store (Production)

**Build App Bundle:**
```cmd
flutter build appbundle --release
```

**Upload to Play Console:**
1. Sign up for Google Play Console ($25 one-time fee)
2. Create new application
3. Upload app bundle
4. Complete store listing
5. Submit for review

### Post-Deployment Checklist

- [ ] Update `app_endpoints.dart` with production URLs
- [ ] Test user registration
- [ ] Test login flow
- [ ] Test WebSocket connections
- [ ] Test message sending/receiving
- [ ] Test image upload (avatars)
- [ ] Test with 10+ concurrent users
- [ ] Monitor error logs on Render
- [ ] Set up custom domain (optional)
## 📚 API Documentation

### Base URLs
- **Development**: `http://10.0.2.2:8000/api/`
- **Production**: `https://vatochito-api.onrender.com/api/`

### Authentication Endpoints

#### Register New User
```http
POST /api/accounts/register/
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}

Response 201:
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "avatar": null,
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Login
```http
POST /api/accounts/login/
Content-Type: application/json

{
  "username": "johndoe",
  "password": "SecurePass123!"
}

Response 200:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "avatar": "http://example.com/media/avatars/user1.jpg"
  }
}
```

#### Refresh Token
```http
POST /api/accounts/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response 200:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### User Endpoints

#### Get Current User Profile
```http
GET /api/accounts/me/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

Response 200:
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "avatar": "http://example.com/media/avatars/user1.jpg"
}
```

#### Update Profile
```http
PATCH /api/accounts/me/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: multipart/form-data

full_name: "John Smith"
avatar: <file>
```

#### Search Users
```http
GET /api/accounts/search/?q=john
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

Response 200:
[
  {
    "id": 2,
    "username": "johndoe2",
    "full_name": "John Doe 2",
    "avatar": null
  }
]
```

### Chat Endpoints

#### Get Conversations List
```http
GET /api/chat/conversations/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

Response 200:
[
  {
    "id": 1,
    "name": "Chat with Jane",
    "is_group": false,
    "last_message": {
      "id": 15,
      "content": "Hello!",
      "created_at": "2025-11-24T10:30:00Z",
      "sender": {
        "id": 2,
        "username": "janedoe",
        "full_name": "Jane Doe"
      }
    },
    "members": [...]
  }
]
```

#### Create Conversation
```http
POST /api/chat/conversations/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "name": "New Chat",
  "is_group": false,
  "member_ids": [2, 3]
}
```

#### Get Messages in Conversation
```http
GET /api/chat/conversations/1/messages/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

Response 200:
[
  {
    "id": 1,
    "content": "Hello!",
    "sender": {
      "id": 1,
      "username": "johndoe",
      "full_name": "John Doe",
      "avatar": null
    },
    "created_at": "2025-11-24T10:00:00Z",
    "is_deleted": false,
    "edited_at": null
  }
]
```

#### Send Message
```http
POST /api/chat/conversations/1/messages/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "content": "Hello, how are you?"
}

Response 201:
{
  "id": 16,
  "content": "Hello, how are you?",
  "sender": {...},
  "created_at": "2025-11-24T10:35:00Z"
}
```

#### Edit Message
```http
PATCH /api/chat/messages/16/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "content": "Hello, how are you doing?"
}
```

#### Delete Message
```http
DELETE /api/chat/messages/16/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

Response 204 No Content
```

### WebSocket Connection

#### Connect to Chat Room
```javascript
ws://10.0.2.2:8000/ws/chat/{conversation_id}/?token={access_token}

// Production
wss://vatochito-api.onrender.com/ws/chat/{conversation_id}/?token={access_token}
```

#### WebSocket Events

**Receive Message:**
```json
{
  "type": "message.new",
  "data": {
    "id": 17,
    "content": "New message",
    "sender": {
      "id": 2,
      "username": "janedoe",
      "full_name": "Jane Doe"
    },
    "created_at": "2025-11-24T10:40:00Z"
  }
}
```

**Message Edited:**
```json
{
  "type": "message.edited",
  "data": {
    "id": 16,
    "content": "Updated message",
    "edited_at": "2025-11-24T10:41:00Z"
  }
}
```

**Message Deleted:**
```json
{
  "type": "message.deleted",
  "data": {
    "id": 16
  }
}
```

For complete API documentation, see [`backend/API_DOCUMENTATION.md`](backend/API_DOCUMENTATION.md)

## 🧪 Testing

### Backend Testing

**Run all tests:**
```cmd
cd backend
python manage.py test
```

**Test specific app:**
```cmd
python manage.py test accounts
python manage.py test chat
```

**Test with coverage:**
```cmd
pip install coverage
coverage run manage.py test
coverage report
coverage html
```

**Available test scripts:**
```cmd
# Test authentication flow
python test_auth_endpoints.py

# Test real-time chat
python test_realtime_chat.py

# Test user search
python test_search_endpoint.py

# Create test data
python create_test_users.py
python create_test_conversation.py
```

### Frontend Testing

**Run unit tests:**
```cmd
flutter test
```

**Run specific test file:**
```cmd
flutter test test/auth_test.dart
```

**Run with coverage:**
```cmd
flutter test --coverage
genhtml coverage/lcov.info -o coverage/html
```

### Manual Testing Checklist

**Authentication:**
- [ ] Register new user
- [ ] Login with credentials
- [ ] Token refresh
- [ ] Logout

**Profile:**
- [ ] View profile
- [ ] Upload avatar
- [ ] Update profile info
- [ ] Delete avatar

**Chat:**
- [ ] Create conversation
- [ ] Send message
- [ ] Receive message in real-time
- [ ] Edit message
- [ ] Delete message
- [ ] Search users
- [ ] View conversation list

**Performance:**
- [ ] Test with 10 concurrent users
- [ ] Message delivery < 100ms
- [ ] WebSocket reconnection works
- [ ] Image upload works

## 📊 Database Schema

### User Model (`accounts.User`)
```python
- id: AutoField
- username: CharField (unique, max_length=150)
- email: EmailField (unique)
- full_name: CharField (max_length=255)
- avatar: ImageField (upload_to='avatars/', blank=True, null=True)
- password: CharField (hashed with PBKDF2)
- date_joined: DateTimeField
- last_login: DateTimeField
```

### Conversation Model (`chat.Conversation`)
```python
- id: AutoField
- name: CharField (max_length=255, blank=True)
- is_group: BooleanField (default=False)
- created_at: DateTimeField (auto_now_add=True)
- updated_at: DateTimeField (auto_now=True)
- members: ManyToManyField (User)
```

### Message Model (`chat.Message`)
```python
- id: AutoField
- conversation: ForeignKey (Conversation)
- sender: ForeignKey (User)
- content: TextField
- created_at: DateTimeField (auto_now_add=True)
- is_deleted: BooleanField (default=False)
- edited_at: DateTimeField (null=True, blank=True)
```

### Attachment Model (`chat.Attachment`)
```python
- id: AutoField
- message: ForeignKey (Message)
- file: FileField (upload_to='uploads/')
- file_type: CharField (max_length=50)
- created_at: DateTimeField (auto_now_add=True)
```

## 🔒 Security Features

### Backend Security
- **JWT Authentication** - Secure token-based auth with refresh tokens
- **Password Hashing** - PBKDF2 with SHA256
- **CORS Protection** - Configured allowed origins
- **SQL Injection Prevention** - Django ORM parameterization
- **XSS Protection** - Django template escaping
- **CSRF Protection** - Django middleware
- **HTTPS Enforcement** - Production settings
- **Secure Headers** - X-Content-Type-Options, X-Frame-Options

### Frontend Security
- **Secure Token Storage** - Flutter Secure Storage with encryption
- **HTTPS Requests** - All API calls over HTTPS in production
- **Input Validation** - Client-side validation before API calls
- **WebSocket WSS** - Encrypted WebSocket connections in production

### Best Practices
1. **Never commit `.env` files** - Add to `.gitignore`
2. **Generate strong SECRET_KEY**:
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```
3. **Regular dependency updates** - `pip list --outdated` and `flutter pub outdated`
4. **Database backups** - Automated backups on Render
5. **Rate limiting** - Consider django-ratelimit for production
6. **Environment-specific configs** - Use separate dev/prod settings

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Migration errors:**
```cmd
python manage.py migrate --run-syncdb
```

**WebSocket connection failed:**
- Check Redis is running: `redis-cli ping`
- Verify Daphne is in INSTALLED_APPS (position 0)
- Check CHANNEL_LAYERS configuration
- For development without Redis, use in-memory channel layer

**Authentication errors:**
- Verify JWT tokens are not expired
- Check ALLOWED_HOSTS includes your domain
- Verify CORS_ALLOWED_ORIGINS includes frontend URL

### Frontend Issues

**Build fails:**
```cmd
flutter clean
flutter pub get
flutter pub upgrade
```

**Code generation fails:**
```cmd
dart run build_runner clean
dart run build_runner build --delete-conflicting-outputs
```

**Connection refused:**
- Verify backend is running: `curl http://10.0.2.2:8000/api/`
- Check `app_endpoints.dart` URLs
- Use `10.0.2.2` for Android emulator (not localhost)
- Disable Windows Firewall temporarily for testing

**WebSocket not connecting:**
- Check WebSocket URL uses correct protocol (ws:// or wss://)
- Verify token is being sent in query params
- Check browser/emulator console for error messages

**Android build errors:**
```cmd
cd android
gradlew clean
cd ..
flutter build apk
```

## 📈 Performance Optimization

### Backend
- **Database Indexing** - Added indexes on frequently queried fields
- **Query Optimization** - Use `select_related()` and `prefetch_related()`
- **Redis Caching** - Channel layers with Redis for WebSocket scaling
- **Static File Compression** - Whitenoise with gzip
- **Connection Pooling** - PostgreSQL connection pooling

### Frontend
- **Lazy Loading** - Load conversations and messages on demand
- **Image Caching** - CachedNetworkImage for avatar caching
- **BLoC Optimization** - Avoid rebuilds with Equatable
- **WebSocket Reconnection** - Automatic reconnection with exponential backoff
- **APK Size** - Use `--split-per-abi` for smaller APKs

### Scalability
- **Horizontal Scaling** - Multiple Daphne instances behind load balancer
- **Redis Sentinel** - High availability for Redis
- **Database Replication** - PostgreSQL read replicas
- **CDN** - CloudFlare for static assets
- **Monitoring** - Sentry for error tracking

## 🎯 Roadmap

### Current Version (v1.0.0)
- ✅ Real-time messaging with WebSockets
- ✅ User authentication (JWT)
- ✅ Profile management with avatars
- ✅ Message edit/delete functionality
- ✅ User search
- ✅ Android mobile app
- ✅ Production deployment ready

### Planned Features (v1.1.0)
- [ ] Push notifications (FCM)
- [ ] Message read receipts
- [ ] Typing indicators
- [ ] Online/offline status
- [ ] Group chat support
- [ ] File attachments (images, documents)
- [ ] Message reactions (emoji)
- [ ] Dark mode

### Future Features (v2.0.0)
- [ ] Voice messages
- [ ] Video calls (WebRTC)
- [ ] End-to-end encryption
- [ ] Message forwarding
- [ ] Stickers & GIFs
- [ ] iOS support
- [ ] Web application
- [ ] Desktop apps (Windows/Mac/Linux)

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Open Pull Request

### Code Standards
- **Python**: Follow PEP 8, use Black formatter
- **Dart**: Follow official Dart style guide, use `flutter format`
- **Commits**: Use conventional commits (feat:, fix:, docs:, etc.)
- **Tests**: Add tests for new features
- **Documentation**: Update README and inline docs

## 📄 License

This project is proprietary software. All rights reserved.

For licensing inquiries, contact: support@vatochito.com

## 🙏 Acknowledgments

- **Flutter Team** - Amazing cross-platform framework
- **Django Team** - Robust web framework
- **Django Channels** - Real-time WebSocket support
- **BLoC Community** - Excellent state management pattern
- **Render** - Reliable hosting platform
- **Material Design** - Beautiful UI/UX guidelines

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/vatochito/issues)
- **Email**: support@vatochito.com
- **Documentation**: See [`backend/API_DOCUMENTATION.md`](backend/API_DOCUMENTATION.md)

## 📊 Project Statistics

- **Backend**: Django 5.0.9, Python 3.11+
- **Frontend**: Flutter 3.x, Dart 3.0+
- **Lines of Code**: ~10,000+ (backend + frontend)
- **Target Users**: 10+ concurrent users
- **Deployment**: Render (backend) + APK (frontend)
- **Development Time**: 2025

---

**Built with ❤️ by the Vatochito one and only hiren patel**

*Making real-time communication simple and secure*
