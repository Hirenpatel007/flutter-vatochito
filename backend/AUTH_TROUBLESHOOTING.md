# 🔧 Authentication Troubleshooting Guide

## Common Login/Register Issues & Solutions

### Issue 1: 404 Not Found on /api/auth/register/

**Problem:** Frontend cannot reach the registration endpoint.

**Solution:**
1. Verify Django server is running:
   ```bash
   cd backend
   python manage.py runserver
   ```

2. Check the URL in browser: http://localhost:8000/api/auth/register/
   - Should return "Method not allowed" (this is correct for GET request)

3. Verify CORS is configured in `backend/vatochito_backend/settings/base.py`:
   ```python
   CORS_ALLOW_ALL_ORIGINS = DEBUG  # Should be True in development
   ```

### Issue 2: CORS Error in Browser Console

**Error:** `Access to XMLHttpRequest has been blocked by CORS policy`

**Solution:**

1. Check that `django-cors-headers` is installed:
   ```bash
   pip install django-cors-headers
   ```

2. Verify CORS middleware is in `settings/base.py`:
   ```python
   MIDDLEWARE = [
       'corsheaders.middleware.CorsMiddleware',  # Must be at the top!
       # ... other middleware
   ]
   ```

3. For development, ensure:
   ```python
   CORS_ALLOW_ALL_ORIGINS = True  # In development only
   CORS_ALLOW_CREDENTIALS = True
   ```

### Issue 3: "Unable to log in with provided credentials"

**Problem:** Login fails even with correct username/password.

**Solutions:**

1. **Check if user exists:**
   ```bash
   python manage.py shell
   from django.contrib.auth import get_user_model
   User = get_user_model()
   User.objects.filter(username='your_username').exists()
   ```

2. **Verify authentication backend:**
   In `settings/base.py`:
   ```python
   AUTHENTICATION_BACKENDS = [
       'accounts.auth_backends.UsernameOrPhoneBackend',
       'django.contrib.auth.backends.ModelBackend',
   ]
   ```

3. **Test password manually:**
   ```bash
   python manage.py shell
   from django.contrib.auth import authenticate
   user = authenticate(username='testuser', password='testpass123')
   print(user)  # Should print user object, not None
   ```

### Issue 4: JWT Token Issues

**Error:** `401 Unauthorized` when accessing protected endpoints.

**Solutions:**

1. **Verify JWT is configured:**
   ```bash
   pip install djangorestframework-simplejwt
   ```

2. **Check settings/base.py:**
   ```python
   REST_FRAMEWORK = {
       "DEFAULT_AUTHENTICATION_CLASSES": (
           "rest_framework_simplejwt.authentication.JWTAuthentication",
       ),
   }
   ```

3. **Check token format in frontend:**
   ```javascript
   // Should be "Bearer <token>"
   Authorization: `Bearer ${token}`
   ```

### Issue 5: Registration Works But Login Fails

**Problem:** Can register but cannot login with the same credentials.

**Solution:**

1. **Check password hashing during registration:**
   In `views.py`, ensure using `create_user()`:
   ```python
   user = User.objects.create_user(  # NOT create()!
       username=username,
       password=password,
       # ...
   )
   ```

2. **Verify in shell:**
   ```bash
   python manage.py shell
   from django.contrib.auth import get_user_model
   User = get_user_model()
   user = User.objects.get(username='testuser')
   user.check_password('testpass123')  # Should return True
   ```

### Issue 6: Frontend Environment Variables Not Working

**Problem:** API calls go to wrong URL or fail.

**Solution:**

1. **Check `.env` file in `frontend/` folder:**
   ```bash
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_WS_URL=ws://localhost:8000
   ```

2. **Restart React development server:**
   ```bash
   # Stop with Ctrl+C, then:
   npm start
   ```

3. **Verify in browser console:**
   ```javascript
   console.log(process.env.REACT_APP_API_URL)
   ```

### Issue 7: "password2" Field Error

**Problem:** Registration form requires password confirmation but backend rejects it.

**Solution:**

The backend doesn't need `password2`. Frontend should only send `password`:

```javascript
// In RegisterPage.js, filter out password2 before sending
const { password2, ...dataToSend } = formData;
await register(dataToSend);
```

Or keep the validation on frontend but don't send password2 to backend.

### Issue 8: Network Error / Connection Refused

**Problem:** Cannot connect to backend at all.

**Solutions:**

1. **Verify backend is running:**
   ```bash
   # Should see "Starting development server at http://127.0.0.1:8000/"
   python manage.py runserver
   ```

2. **Check port 8000 is not in use:**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

3. **Try explicit IP:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

4. **Update frontend .env:**
   ```bash
   REACT_APP_API_URL=http://127.0.0.1:8000
   ```

## Quick Test Commands

### Test Backend Directly (Using curl or Python)

**1. Test Registration:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

**2. Test Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

**3. Test Get User (replace TOKEN):**
```bash
curl http://localhost:8000/api/auth/user/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Test Using Python Script

Run the test script:
```bash
cd backend
python test_auth_endpoints.py
```

This will test:
- Registration
- Login
- Get current user
- Token validation

## Browser Console Debugging

Open browser DevTools (F12) and check:

1. **Network Tab:**
   - Check request URL (should be http://localhost:8000/api/auth/...)
   - Check request method (POST for login/register)
   - Check request headers (Content-Type: application/json)
   - Check request payload (your form data)
   - Check response status (200 OK, 201 Created, or error code)
   - Check response body (error messages)

2. **Console Tab:**
   - Look for CORS errors
   - Look for JavaScript errors
   - Check API URL: `console.log(process.env.REACT_APP_API_URL)`

3. **Application Tab:**
   - Check localStorage for tokens
   - Should see `access_token` and `refresh_token` after successful login

## Common Error Messages & Fixes

| Error Message | Cause | Fix |
|--------------|-------|-----|
| "This field is required" | Missing required field | Add all required fields: username, password |
| "A user with that username already exists" | Duplicate username | Use different username or delete existing user |
| "Ensure this field has no more than X characters" | Field too long | Shorten the input |
| "Enter a valid email address" | Invalid email format | Check email format |
| "Unable to log in with provided credentials" | Wrong username/password | Check credentials or password hashing |
| "Token is invalid or expired" | JWT token expired | Login again to get new token |
| "Method not allowed" | Wrong HTTP method | Check if using POST for login/register |
| "Not found" | Wrong URL | Verify endpoint URL path |

## Debug Mode Checklist

When debugging authentication:

- [ ] Backend server is running (port 8000)
- [ ] Frontend server is running (port 3000)
- [ ] Redis is running (for WebSocket)
- [ ] Database migrations are applied
- [ ] CORS is enabled in backend
- [ ] Environment variables are set correctly
- [ ] No firewall blocking ports
- [ ] Browser console shows no CORS errors
- [ ] Network tab shows requests being sent
- [ ] Backend terminal shows incoming requests
- [ ] Tokens are being stored in localStorage
- [ ] API responses contain `access` and `refresh` tokens

## Still Having Issues?

1. **Clear browser cache and localStorage:**
   - Open DevTools (F12)
   - Application tab → Local Storage → Clear All
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

2. **Restart all services:**
   ```bash
   # Stop all (Ctrl+C in each terminal)
   # Then start fresh:
   
   # Terminal 1: Backend
   cd backend
   python manage.py runserver
   
   # Terminal 2: Frontend
   cd frontend
   npm start
   ```

3. **Check Django logs:**
   Look at the terminal running `python manage.py runserver` for error messages.

4. **Enable Django debug mode:**
   In `.env`:
   ```
   DJANGO_DEBUG=True
   ```

5. **Run migrations:**
   ```bash
   cd backend
   python manage.py migrate
   ```

6. **Create test user manually:**
   ```bash
   python manage.py createsuperuser
   ```
   Then try logging in with these credentials.

## Working Example

Here's a minimal working example:

**Backend endpoint test:**
```bash
# Should return JWT tokens
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_admin_password"}'
```

**Expected response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

If you get this response, your backend is working correctly!

---

**Need more help?** Check the main [README.md](../README.md) or [QUICKSTART.md](../QUICKSTART.md)
