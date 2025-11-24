# Backend Test Instructions

## Current Status
✅ Backend server running at: http://127.0.0.1:8000/
✅ Database migrations applied
✅ Admin user created (username: admin, password: admin123)

## Test the API Endpoints

### 1. Access API Documentation
- Swagger UI: http://127.0.0.1:8000/api/docs/
- API Schema: http://127.0.0.1:8000/api/schema/

### 2. Admin Panel
- URL: http://127.0.0.1:8000/admin/
- Username: admin
- Password: admin123

### 3. Test Authentication

**Register a new user:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"testuser\", \"password\": \"testpass123\", \"email\": \"test@example.com\"}"
```

**Login:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"testuser\", \"password\": \"testpass123\"}"
```

### 4. Test Chat Endpoints (requires authentication)

**Get conversations:**
```bash
curl -X GET http://127.0.0.1:8000/api/chat/conversations/ ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Notes
- Backend uses SQLite database (db.sqlite3) for development
- Redis/Celery not required for basic testing
- WebSocket endpoint: ws://127.0.0.1:8000/ws/conversations/{id}/
