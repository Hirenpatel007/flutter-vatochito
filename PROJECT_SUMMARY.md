# Vatochito - Full-Stack Chat Application

## Project Structure

### Backend (Django REST + Channels)
- **Location**: `backend/`
- **Server**: Running at `http://127.0.0.1:8000/`
- **Database**: SQLite (development)
- **Admin**: `http://127.0.0.1:8000/admin/` (admin/admin123)

#### API Endpoints
- `POST /api/auth/` - Register new user
- `POST /api/auth/login/` - Login
- `POST /api/auth/refresh/` - Refresh JWT token  
- `GET /api/auth/profile/me/` - Get current user profile
- `GET /api/chat/conversations/` - List user conversations
- `GET /api/chat/conversations/{id}/messages/` - Get conversation messages
- `POST /api/chat/conversations/{id}/messages/` - Send message
- `ws://127.0.0.1:8000/ws/conversations/{id}/` - WebSocket for real-time chat

#### Features Implemented
✅ Custom User model with phone number support
✅ JWT authentication with token refresh
✅ Phone or username login
✅ Conversation & message models
✅ Message receipts (sent/delivered/read)
✅ File attachments support
✅ WebSocket real-time messaging
✅ Admin panel

### Frontend (Flutter)
- **Location**: `lib/`
- **Platforms**: Windows, Android, iOS, Web, Linux, macOS
- **State Management**: flutter_bloc
- **Navigation**: go_router
- **HTTP Client**: dio
- **WebSocket**: web_socket_channel

#### Architecture
```
lib/
├── main.dart                          # Entry point
└── src/
    ├── app/                           # App bootstrap & initialization
    ├── config/                        # Theme, routing, constants
    ├── core/                          # Network, storage, utilities
    └── features/
        ├── auth/                      # Authentication
        │   ├── data/                  # Models, repositories
        │   └── presentation/          # Bloc, pages, widgets
        └── chat/                      # Messaging
            ├── data/                  # Models, repositories
            └── presentation/          # Cubit, pages, widgets
```

#### Features Implemented
✅ Login/Register screens
✅ JWT token management with auto-refresh
✅ Conversation list
✅ Real-time chat room
✅ Message bubbles with timestamps
✅ WebSocket connection for live updates
✅ Offline-first architecture ready
✅ Multi-platform support

## Running the Application

### Backend
```bash
cd backend
venv\Scripts\activate  # Windows
python manage.py runserver
```

### Frontend
```bash
flutter pub get
flutter run -d windows  # or chrome, android, etc.
```

## Default Credentials
- **Admin**: admin / admin123
- **Test User**: testuser / testpass123 (create via API)

## Next Steps
1. ✅ Backend server running
2. ✅ Frontend building
3. ⏳ Test authentication flow
4. ⏳ Test real-time messaging
5. ⏳ Add Redis for WebSocket (optional)
6. ⏳ Add push notifications
7. ⏳ Deploy to production
