# Vatochito Deployment Guide

## 🚀 Quick Deployment Guide - FREE Options

### Table of Contents
1. [Backend Deployment (Choose One)](#backend-deployment)
   - [Option 1: Render.com (Recommended)](#option-1-rendercom)
   - [Option 2: Railway.app](#option-2-railwayapp)
   - [Option 3: Fly.io](#option-3-flyio)
   - [Option 4: PythonAnywhere](#option-4-pythonanywhere)
2. [Frontend Deployment (Choose One)](#frontend-deployment)
   - [Web Deployment](#web-deployment)
   - [Mobile Deployment](#mobile-deployment)
3. [Database Setup](#database-setup)
4. [Environment Configuration](#environment-configuration)
5. [Post-Deployment](#post-deployment)

---

## Backend Deployment

### Option 1: Render.com (⭐ RECOMMENDED)

**Why Choose Render?**
- ✅ Free tier available
- ✅ PostgreSQL database included
- ✅ Automatic HTTPS
- ✅ WebSocket support
- ✅ Easy deployment from GitHub
- ❌ 750 hours/month limit (spins down after 15min inactivity)

#### Step-by-Step:

1. **Prepare Your Code**
```bash
cd backend

# Add gunicorn to requirements.txt
echo "gunicorn==21.2.0" >> requirements.txt
```

2. **Create `build.sh` script** (in `backend/` directory):
```bash
#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
```

Make it executable:
```bash
chmod +x build.sh
```

3. **Update Production Settings** (`backend/vatochito_backend/settings/production.py`):
```python
from .base import *

DEBUG = False

# Render.com specific
ALLOWED_HOSTS = ['.onrender.com', 'your-custom-domain.com']
CSRF_TRUSTED_ORIGINS = ['https://your-app.onrender.com']

# Database from environment variable
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=env('DATABASE_URL'),
        conn_max_age=600
    )
}

# CORS for your frontend
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://your-frontend.vercel.app',
    'https://your-custom-domain.com',
]

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

4. **Push to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/vatochito.git
git push -u origin main
```

5. **Deploy on Render**:
   - Go to [render.com](https://render.com) and sign up
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `vatochito-backend`
     - **Region**: Choose closest to you
     - **Branch**: `main`
     - **Root Directory**: `backend`
     - **Runtime**: `Python 3`
     - **Build Command**: `./build.sh`
     - **Start Command**: `gunicorn vatochito_backend.wsgi:application`
     - **Plan**: `Free`

6. **Add Environment Variables** in Render Dashboard:
```
DJANGO_SECRET_KEY=<generate-new-secret-key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.onrender.com
DJANGO_SETTINGS_MODULE=vatochito_backend.settings.production
DATABASE_URL=<auto-filled-by-render>
REDIS_URL=<from-redis-service>
```

7. **Create PostgreSQL Database**:
   - In Render dashboard, click "New +" → "PostgreSQL"
   - Name: `vatochito-db`
   - Connect it to your web service
   - Copy the "Internal Database URL" to `DATABASE_URL` environment variable

8. **Create Redis Instance** (optional, for WebSocket):
   - Click "New +" → "Redis"
   - Name: `vatochito-redis`
   - Copy the "Internal Redis URL" to `REDIS_URL` environment variable

9. **Deploy**: Click "Create Web Service" and wait for deployment

Your backend will be live at: `https://vatochito-backend.onrender.com`

---

### Option 2: Railway.app

**Why Choose Railway?**
- ✅ Generous free tier ($5 credit/month)
- ✅ PostgreSQL & Redis built-in
- ✅ Automatic deployments
- ✅ WebSocket support
- ❌ Requires credit card verification

#### Step-by-Step:

1. **Install Railway CLI**:
```bash
npm install -g @railway/cli
# or
curl -fsSL https://railway.app/install.sh | sh
```

2. **Login and Initialize**:
```bash
cd backend
railway login
railway init
```

3. **Add Services**:
```bash
railway add --database postgres
railway add --database redis
```

4. **Deploy**:
```bash
railway up
```

5. **Set Environment Variables**:
```bash
railway variables set DJANGO_SECRET_KEY=your-secret-key
railway variables set DJANGO_DEBUG=False
railway variables set DJANGO_SETTINGS_MODULE=vatochito_backend.settings.production
```

6. **Configure Start Command** in `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn vatochito_backend.wsgi:application",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Your backend will be at: `https://vatochito-production.up.railway.app`

---

### Option 3: Fly.io

**Why Choose Fly.io?**
- ✅ Free tier (3 VMs)
- ✅ WebSocket support
- ✅ Global deployment
- ✅ Excellent performance
- ❌ Credit card required

#### Step-by-Step:

1. **Install flyctl**:
```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# Mac/Linux
curl -L https://fly.io/install.sh | sh
```

2. **Login and Launch**:
```bash
cd backend
flyctl auth login
flyctl launch
```

3. **Configure `fly.toml`**:
```toml
app = "vatochito-backend"
primary_region = "iad"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8000"
  DJANGO_SETTINGS_MODULE = "vatochito_backend.settings.production"

[[services]]
  protocol = "tcp"
  internal_port = 8000

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

  [services.concurrency]
    type = "connections"
    hard_limit = 25
    soft_limit = 20

[[services.tcp_checks]]
  interval = "15s"
  timeout = "2s"
  grace_period = "1s"
```

4. **Add PostgreSQL**:
```bash
flyctl postgres create
flyctl postgres attach --app vatochito-backend
```

5. **Set Secrets**:
```bash
flyctl secrets set DJANGO_SECRET_KEY=your-secret-key
flyctl secrets set DJANGO_DEBUG=False
```

6. **Deploy**:
```bash
flyctl deploy
```

Your backend will be at: `https://vatochito-backend.fly.dev`

---

### Option 4: PythonAnywhere

**Why Choose PythonAnywhere?**
- ✅ 100% free tier forever
- ✅ Django-optimized
- ✅ Easy setup
- ❌ No WebSocket support (use polling fallback)
- ❌ Limited resources

#### Step-by-Step:

1. **Sign up** at [pythonanywhere.com](https://www.pythonanywhere.com)

2. **Upload Code**:
   - Use Git: `git clone https://github.com/yourusername/vatochito.git`
   - Or upload via Files tab

3. **Create Virtual Environment**:
```bash
mkvirtualenv --python=/usr/bin/python3.10 vatochito
cd vatochito/backend
pip install -r requirements.txt
```

4. **Configure Web App**:
   - Go to "Web" tab → "Add a new web app"
   - Choose "Manual configuration"
   - Python version: 3.10
   - Working directory: `/home/yourusername/vatochito/backend`

5. **Configure WSGI**:
```python
import os
import sys

path = '/home/yourusername/vatochito/backend'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'vatochito_backend.settings.production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

6. **Setup Database**:
```bash
python manage.py migrate
python manage.py createsuperuser
```

7. **Static Files**:
   - In Web tab, set Static files:
   - URL: `/static/`
   - Directory: `/home/yourusername/vatochito/backend/staticfiles/`

8. **Reload Web App**

Your backend will be at: `https://yourusername.pythonanywhere.com`

---

## Frontend Deployment

### Web Deployment

#### Option 1: Vercel (⭐ RECOMMENDED for Web)

1. **Build for Web**:
```bash
flutter build web --release
```

2. **Create `vercel.json`** in project root:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "build/web/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/build/web/$1"
    }
  ]
}
```

3. **Update API Endpoint** (`lib/src/core/constants/app_endpoints.dart`):
```dart
static const apiBaseUrl = 'https://your-backend.onrender.com/api';
static const websocketBaseUrl = 'wss://your-backend.onrender.com/ws';
```

4. **Deploy**:
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

Or use Vercel Dashboard:
- Go to [vercel.com](https://vercel.com)
- Import your GitHub repository
- Build settings:
  - **Framework Preset**: Other
  - **Build Command**: `flutter build web --release`
  - **Output Directory**: `build/web`
- Deploy

Your app will be at: `https://vatochito.vercel.app`

---

#### Option 2: Netlify

1. **Build**:
```bash
flutter build web --release
cd build/web
echo "/*    /index.html   200" > _redirects
```

2. **Deploy**:
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=build/web
```

Or drag & drop `build/web` folder on [netlify.com](https://app.netlify.com)

---

#### Option 3: Firebase Hosting

1. **Install Firebase CLI**:
```bash
npm install -g firebase-tools
```

2. **Login and Initialize**:
```bash
firebase login
firebase init hosting
```

3. **Configure `firebase.json`**:
```json
{
  "hosting": {
    "public": "build/web",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

4. **Build and Deploy**:
```bash
flutter build web --release
firebase deploy --only hosting
```

---

### Mobile Deployment

#### Android - Google Play Store

1. **Create Keystore**:
```bash
keytool -genkey -v -keystore ~/vatochito-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias vatochito
```

2. **Configure Signing** (`android/key.properties`):
```properties
storePassword=<your-password>
keyPassword=<your-password>
keyAlias=vatochito
storeFile=<path-to-keystore>
```

3. **Update `android/app/build.gradle`**:
```gradle
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
        }
    }
}
```

4. **Build APK/App Bundle**:
```bash
# Build APK
flutter build apk --release

# Build App Bundle (recommended)
flutter build appbundle --release
```

5. **Upload to Google Play Console**:
   - Create developer account ($25 one-time)
   - Create app listing
   - Upload `build/app/outputs/bundle/release/app-release.aab`
   - Fill in store listing details
   - Submit for review

---

#### iOS - App Store (Mac only)

1. **Configure Xcode**:
   - Open `ios/Runner.xcworkspace` in Xcode
   - Select team
   - Configure bundle ID

2. **Build**:
```bash
flutter build ios --release
```

3. **Archive and Upload**:
   - Open Xcode → Product → Archive
   - Upload to App Store Connect
   - Submit for review

---

#### Windows - Microsoft Store

1. **Build**:
```bash
flutter build windows --release
```

2. **Package with MSIX**:
```bash
flutter pub add msix
flutter pub run msix:create
```

3. **Upload to Microsoft Store**:
   - Create developer account ($19/year)
   - Create app submission
   - Upload MSIX file
   - Submit for certification

---

## Database Setup

### PostgreSQL (Production)

For Render.com/Railway.app (auto-configured):
- Database URL is automatically set
- Migrations run on deployment

For manual setup:
```bash
# Create database
createdb vatochito_db

# Update DATABASE_URL
export DATABASE_URL="postgresql://user:password@localhost:5432/vatochito_db"

# Run migrations
python manage.py migrate
```

---

## Environment Configuration

### Backend Environment Variables

#### Required:
```env
DJANGO_SECRET_KEY=<generate-with-get_random_secret_key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.onrender.com,your-domain.com
DJANGO_SETTINGS_MODULE=vatochito_backend.settings.production
DATABASE_URL=postgresql://user:pass@host:port/db
```

#### Optional:
```env
REDIS_URL=redis://host:port/0
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}

# For S3/Cloud Storage
DEFAULT_FILE_STORAGE=storages.backends.s3boto3.S3Boto3Storage
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=us-east-1

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Generate Secret Key:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## Post-Deployment

### 1. Create Superuser
```bash
# Render.com
render ssh
python manage.py createsuperuser

# Railway.app
railway run python manage.py createsuperuser

# Fly.io
flyctl ssh console
python manage.py createsuperuser
```

### 2. Test API
```bash
curl https://your-backend.onrender.com/api/
```

### 3. Update Frontend API URLs
```dart
// lib/src/core/constants/app_endpoints.dart
static const apiBaseUrl = 'https://your-backend.onrender.com/api';
static const websocketBaseUrl = 'wss://your-backend.onrender.com/ws';
```

### 4. Enable HTTPS
- Most platforms provide automatic HTTPS
- For custom domains, add SSL certificate

### 5. Setup Monitoring
- Enable logging in Django
- Use Sentry for error tracking
- Monitor performance metrics

---

## Troubleshooting

### Backend Issues

**"Application failed to respond":**
- Check logs: `render logs` or `railway logs`
- Verify `ALLOWED_HOSTS` includes your domain
- Check `DATABASE_URL` is correct

**Database connection failed:**
- Verify PostgreSQL is running
- Check database credentials
- Ensure IP whitelist includes your server

**Static files not loading:**
- Run `python manage.py collectstatic`
- Check `STATIC_ROOT` and `STATIC_URL`
- Verify WhiteNoise is installed

**WebSocket connection failed:**
- Ensure Redis is running
- Check WebSocket route configuration
- Verify CORS settings

### Frontend Issues

**API connection failed:**
- Check `app_endpoints.dart` URLs
- Verify CORS settings on backend
- Test API manually with curl/Postman

**Build failed:**
- Run `flutter clean`
- Delete `build/` folder
- Run `flutter pub get`
- Try again

---

## Cost Breakdown (Monthly)

### Free Option:
- **Backend**: Render.com Free Tier ($0)
- **Database**: Render PostgreSQL Free ($0)
- **Frontend**: Vercel Free Tier ($0)
- **Total**: **$0/month**

### Paid Option (Better performance):
- **Backend**: Render Starter ($7)
- **Database**: Render PostgreSQL Starter ($7)
- **Redis**: Render Redis Starter ($7)
- **Frontend**: Vercel Pro ($20)
- **Total**: **$41/month**

---

## Support

For deployment help:
- **Documentation**: Check README.md
- **Issues**: GitHub Issues
- **Community**: Discord/Slack channel

---

**Good luck with your deployment! 🚀**
