# Authentication Fix Guide

## Issues Fixed

### 1. URL Configuration
- ✅ Fixed AuthViewSet URL mappings in `accounts/urls.py`
- ✅ Properly mapped GET and PATCH methods to user endpoint

### 2. Registration
- ✅ Added `password2` field for password confirmation
- ✅ Added password validation to check if passwords match
- ✅ Registration now returns user data along with tokens

### 3. Login
- ✅ Login now returns user data along with tokens
- ✅ Updates user online status on login
- ✅ Updates last_seen_at timestamp

## Testing

### Option 1: Django Test (Quick)
```bash
cd backend
python quick_test.py
```

### Option 2: Manual API Test
```bash
cd backend
python test_auth_endpoints.py
```

### Option 3: Test with cURL

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"testpass123\",\"password2\":\"testpass123\"}"
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"password\":\"testpass123\"}"
```

**Get User:**
```bash
curl -X GET http://localhost:8000/api/auth/user/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Frontend Updates Needed

Update your frontend to handle the new response format:

### Before:
```javascript
const response = await authService.login(username, password);
// response.data = { access: "...", refresh: "..." }
```

### After:
```javascript
const response = await authService.login(username, password);
// response.data = { user: {...}, access: "...", refresh: "..." }
```

### Update authService.js:

```javascript
async login(username, password) {
  const response = await api.post('/auth/login/', { username, password });
  if (response.data.access) {
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    localStorage.setItem('user', JSON.stringify(response.data.user));
  }
  return response.data;
},

async register(userData) {
  const response = await api.post('/auth/register/', userData);
  if (response.data.access) {
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    localStorage.setItem('user', JSON.stringify(response.data.user));
  }
  return response.data;
},
```

### Update AuthContext.js:

```javascript
const login = async (username, password) => {
  const data = await authService.login(username, password);
  setUser(data.user);  // User data now included in response
  return data;
};

const register = async (userData) => {
  const data = await authService.register(userData);
  // Now automatically logged in after registration
  if (data.user) {
    setUser(data.user);
  }
  return data;
};
```

## API Response Format

### Registration Response:
```json
{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "display_name": "Test User",
    "phone_number": "+1234567890",
    "avatar": null,
    "status_message": "",
    "is_online": false,
    "last_seen_at": null
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Login Response:
```json
{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "display_name": "Test User",
    "phone_number": "+1234567890",
    "avatar": null,
    "status_message": "",
    "is_online": true,
    "last_seen_at": "2025-11-03T10:30:00Z"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Troubleshooting

### Error: "Passwords do not match"
- Make sure you're sending both `password` and `password2` fields
- Both must have the same value

### Error: "This field may not be blank"
- Check that username and password are provided
- Email is optional

### Error: "Unable to log in with provided credentials"
- Verify username and password are correct
- Make sure user exists (register first)

### Error: 401 Unauthorized
- Token expired - use refresh token
- Token invalid - login again

## Next Steps

1. ✅ Test registration endpoint
2. ✅ Test login endpoint
3. ✅ Test get user endpoint
4. ✅ Update frontend services
5. ✅ Update frontend context
6. ✅ Test full auth flow

## Command Summary

```bash
# Run backend
cd backend
python manage.py runserver

# In another terminal, test auth
cd backend
python quick_test.py

# Or test with external requests
cd backend
python test_auth_endpoints.py
```
