# 🚀 Vatochito Production Deployment Guide

## Complete Guide for Launching Real WhatsApp-Like Chat App

This guide will help you deploy Vatochito with **real Google OAuth and Phone/SMS OTP authentication** for production use.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Google OAuth Setup](#google-oauth-setup)
3. [Twilio SMS OTP Setup](#twilio-sms-otp-setup)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Domain & SSL Setup](#domain--ssl-setup)
7. [Testing Production](#testing-production)
8. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 1. Prerequisites

### Required Accounts
- ✅ **Google Cloud Console** (for OAuth)
- ✅ **Twilio Account** (for SMS OTP)
- ✅ **AWS Account** (for S3 file storage)
- ✅ **Domain Name** (e.g., vatochito.com)
- ✅ **Hosting**: Choose one:
  - **Backend**: Heroku, AWS EC2, DigitalOcean, Railway
  - **Frontend**: Vercel, Netlify, AWS S3+CloudFront
- ✅ **Database**: PostgreSQL (managed service or self-hosted)
- ✅ **Redis**: Redis Cloud, AWS ElastiCache, or self-hosted

---

## 2. Google OAuth Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Create Project"**
3. Name: `Vatochito`
4. Click **"Create"**

### Step 2: Enable Google+ API

1. In your project, go to **"APIs & Services" → "Library"**
2. Search for **"Google+ API"**
3. Click **"Enable"**

### Step 3: Create OAuth Credentials

1. Go to **"APIs & Services" → "Credentials"**
2. Click **"Create Credentials" → "OAuth Client ID"**
3. If prompted, configure **OAuth Consent Screen**:
   - **App name**: Vatochito
   - **User support email**: your-email@gmail.com
   - **Developer contact**: your-email@gmail.com
   - Add scopes: `email`, `profile`, `openid`
   - Add test users (for testing)
4. Create **OAuth Client ID**:
   - **Application type**: Web application
   - **Name**: Vatochito Web
   - **Authorized JavaScript origins**:
     ```
     http://localhost:3000
     https://vatochito.com
     https://www.vatochito.com
     ```
   - **Authorized redirect URIs**:
     ```
     http://localhost:3000/auth/google/callback
     https://vatochito.com/auth/google/callback
     ```
5. Click **"Create"**
6. **Copy** `Client ID` and `Client Secret`

### Step 4: Add to Environment Variables

Add to your `.env` file:
```env
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
```

---

## 3. Twilio SMS OTP Setup

### Step 1: Create Twilio Account

1. Go to [Twilio.com](https://www.twilio.com/)
2. **Sign Up** for free trial (you get $15 credit)
3. Verify your email and phone number

### Step 2: Get Phone Number

1. In Twilio Console, go to **"Phone Numbers" → "Manage" → "Buy a number"**
2. Choose country (e.g., India +91)
3. Filter by: **Voice**, **SMS**, **MMS**
4. Buy number (costs ~$1/month)
5. **Copy** your Twilio phone number

### Step 3: Get API Credentials

1. Go to [Twilio Console Dashboard](https://console.twilio.com/)
2. Find **"Account Info"** section
3. **Copy**:
   - Account SID
   - Auth Token

### Step 4: Add to Environment Variables

Add to your `.env` file:
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

### Twilio Pricing (India)
- **SMS**: ₹0.75 per message (~$0.009)
- **Phone Number**: ~₹80/month ($1)
- **Free Trial**: $15 credit (can send ~1600 SMS)

---

## 4. Backend Deployment

### Option A: Deploy to Heroku (Easiest)

#### 1. Install Heroku CLI
```bash
# Download from: https://devcenter.heroku.com/articles/heroku-cli
```

#### 2. Login to Heroku
```bash
heroku login
```

#### 3. Create Heroku App
```bash
cd backend
heroku create vatochito-api
```

#### 4. Add PostgreSQL & Redis
```bash
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
```

#### 5. Set Environment Variables
```bash
heroku config:set SECRET_KEY="your-super-secret-key"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="vatochito-api.herokuapp.com"
heroku config:set GOOGLE_OAUTH_CLIENT_ID="your-client-id"
heroku config:set GOOGLE_OAUTH_CLIENT_SECRET="your-secret"
heroku config:set TWILIO_ACCOUNT_SID="ACxxxxx"
heroku config:set TWILIO_AUTH_TOKEN="your-token"
heroku config:set TWILIO_PHONE_NUMBER="+1234567890"
heroku config:set AWS_ACCESS_KEY_ID="your-key"
heroku config:set AWS_SECRET_ACCESS_KEY="your-secret"
heroku config:set AWS_STORAGE_BUCKET_NAME="vatochito-media"
```

#### 6. Create `Procfile`
Create `backend/Procfile`:
```
web: daphne vatochito_backend.asgi:application --port $PORT --bind 0.0.0.0
worker: celery -A vatochito_backend worker --loglevel=info
```

#### 7. Create `runtime.txt`
Create `backend/runtime.txt`:
```
python-3.13.0
```

#### 8. Deploy
```bash
git add .
git commit -m "Production deployment"
git push heroku main
```

#### 9. Run Migrations
```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

#### 10. Open App
```bash
heroku open
```

### Option B: Deploy to AWS EC2

#### 1. Launch EC2 Instance
- **Instance Type**: t3.small or t3.medium
- **OS**: Ubuntu 22.04 LTS
- **Security Groups**: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

#### 2. SSH into Server
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

#### 3. Install Dependencies
```bash
sudo apt update
sudo apt install -y python3.11 python3-pip python3-venv
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y redis-server
sudo apt install -y nginx certbot python3-certbot-nginx
```

#### 4. Setup Project
```bash
cd /var/www
sudo git clone https://github.com/yourusername/vatochito.git
cd vatochito/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn daphne
```

#### 5. Setup PostgreSQL
```bash
sudo -u postgres psql
CREATE DATABASE vatochito_db;
CREATE USER vatochito_user WITH PASSWORD 'your-password';
ALTER ROLE vatochito_user SET client_encoding TO 'utf8';
ALTER ROLE vatochito_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE vatochito_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE vatochito_db TO vatochito_user;
\q
```

#### 6. Create `.env` File
```bash
nano .env
```
Paste all your environment variables from `.env.production`

#### 7. Run Migrations
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 8. Setup Gunicorn Service
```bash
sudo nano /etc/systemd/system/vatochito.service
```

Paste:
```ini
[Unit]
Description=Vatochito Django App
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/vatochito/backend
Environment="PATH=/var/www/vatochito/backend/venv/bin"
ExecStart=/var/www/vatochito/backend/venv/bin/daphne -b 0.0.0.0 -p 8000 vatochito_backend.asgi:application

[Install]
WantedBy=multi-user.target
```

#### 9. Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl start vatochito
sudo systemctl enable vatochito
sudo systemctl status vatochito
```

#### 10. Setup Nginx
```bash
sudo nano /etc/nginx/sites-available/vatochito
```

Paste:
```nginx
server {
    listen 80;
    server_name api.vatochito.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /static/ {
        alias /var/www/vatochito/backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/vatochito/backend/media/;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/vatochito /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 11. Get SSL Certificate
```bash
sudo certbot --nginx -d api.vatochito.com
```

---

## 5. Frontend Deployment

### Option A: Deploy to Vercel (Recommended)

#### 1. Install Vercel CLI
```bash
npm install -g vercel
```

#### 2. Login
```bash
vercel login
```

#### 3. Configure Environment
Create `frontend/.env.production`:
```env
REACT_APP_API_URL=https://api.vatochito.com
REACT_APP_WS_URL=wss://api.vatochito.com
REACT_APP_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

#### 4. Deploy
```bash
cd frontend
vercel --prod
```

#### 5. Add Domain
- Go to Vercel Dashboard
- Project Settings → Domains
- Add `vatochito.com` and `www.vatochito.com`

### Option B: Deploy to Netlify

#### 1. Build Production
```bash
cd frontend
npm run build
```

#### 2. Deploy via CLI
```bash
npm install -g netlify-cli
netlify login
netlify deploy --prod --dir=build
```

#### 3. Configure Environment
- Go to Netlify Dashboard
- Site Settings → Environment Variables
- Add all `REACT_APP_*` variables

---

## 6. Domain & SSL Setup

### 1. Buy Domain
- **Namecheap**, **GoDaddy**, or **Google Domains**
- Cost: ~$10-15/year

### 2. Configure DNS
Add these DNS records:

```
Type    Name    Value                       TTL
A       @       your-backend-server-ip      3600
A       www     your-backend-server-ip      3600
A       api     your-backend-server-ip      3600
CNAME   www     vatochito.com               3600
```

For Vercel frontend:
```
CNAME   @       cname.vercel-dns.com        3600
```

### 3. Wait for Propagation
- DNS changes take 24-48 hours
- Check with: `nslookup vatochito.com`

---

## 7. Testing Production

### Test Google OAuth
1. Go to `https://vatochito.com/login`
2. Click **"Sign in with Google"**
3. Complete OAuth flow
4. Should redirect with JWT tokens

### Test Phone OTP
```bash
curl -X POST https://api.vatochito.com/api/auth/phone/request-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'
```

Expected response:
```json
{
  "message": "OTP sent successfully",
  "phone_number": "+919876543210",
  "expires_in": 600
}
```

### Test File Upload
1. Login
2. Start a chat
3. Upload image/video/document
4. Files should be stored in AWS S3

### Test WebSocket
1. Open two browser windows
2. Login as different users
3. Send messages
4. Should see real-time updates

---

## 8. Monitoring & Maintenance

### Setup Error Tracking (Sentry)

1. Sign up at [Sentry.io](https://sentry.io/)
2. Create project: "Vatochito"
3. Get DSN key
4. Add to `.env`:
```env
SENTRY_DSN=https://your-dsn@sentry.io/project-id
```

### Monitor Server Health

**Install monitoring:**
```bash
pip install django-prometheus
```

**Add to `settings.py`:**
```python
INSTALLED_APPS += ['django_prometheus']
MIDDLEWARE = ['django_prometheus.middleware.PrometheusBeforeMiddleware'] + MIDDLEWARE
MIDDLEWARE += ['django_prometheus.middleware.PrometheusAfterMiddleware']
```

### Setup Logs

**Backend logs:**
```bash
tail -f /var/www/vatochito/backend/logs/django.log
tail -f /var/www/vatochito/backend/logs/errors.log
```

**Nginx logs:**
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Backup Database

**Daily backup script:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump vatochito_db > /backups/vatochito_$DATE.sql
# Upload to S3
aws s3 cp /backups/vatochito_$DATE.sql s3://vatochito-backups/
```

### Update & Maintenance

**Update code:**
```bash
cd /var/www/vatochito
git pull origin main
source backend/venv/bin/activate
pip install -r backend/requirements.txt
python backend/manage.py migrate
python backend/manage.py collectstatic --noinput
sudo systemctl restart vatochito
```

---

## 9. Cost Estimation

### Monthly Costs (India)

| Service | Plan | Cost |
|---------|------|------|
| **Domain** | .com domain | ₹80-100/month |
| **Backend Hosting** | Heroku Hobby / AWS t3.small | ₹400-700/month |
| **Database** | Heroku PostgreSQL / RDS | ₹400/month |
| **Redis** | Heroku Redis / ElastiCache | ₹300/month |
| **Twilio SMS** | Pay-as-you-go | ₹0.75/SMS |
| **AWS S3** | Standard storage | ₹100-300/month |
| **Frontend (Vercel)** | Hobby plan | Free-₹1500/month |
| **SSL Certificate** | Let's Encrypt | Free |
| **Total** | | **₹1,200-3,000/month** |

**Note**: For 500+ concurrent users, upgrade to:
- Backend: t3.medium (₹1,500/month)
- Database: Larger instance (₹1,500/month)
- Redis: Cluster mode (₹1,000/month)

---

## 10. Launch Checklist

### Pre-Launch
- [ ] Google OAuth configured and tested
- [ ] Twilio SMS OTP working
- [ ] AWS S3 file uploads working
- [ ] PostgreSQL database optimized
- [ ] Redis cache working
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] Environment variables set
- [ ] Database migrations run
- [ ] Static files collected
- [ ] Error tracking (Sentry) configured
- [ ] Backup system setup

### Testing
- [ ] User registration working
- [ ] Login with Google working
- [ ] Login with Phone OTP working
- [ ] Real-time chat working
- [ ] File uploads working (images, videos, audio, docs)
- [ ] WebSocket stable connection
- [ ] Mobile responsive design tested
- [ ] Performance tested with 100+ users
- [ ] Security headers configured
- [ ] Rate limiting working

### Go Live!
- [ ] Announce on social media
- [ ] Monitor error logs
- [ ] Watch server metrics
- [ ] Be ready for support requests

---

## 🎉 Congratulations!

Your Vatochito WhatsApp-like chat app is now **LIVE** with real authentication!

**Next Steps:**
1. Add more users
2. Monitor performance
3. Collect feedback
4. Add new features
5. Scale as needed

---

## Support

For issues:
- Check logs: `/var/www/vatochito/backend/logs/`
- Monitor Sentry for errors
- Review Django admin: `https://api.vatochito.com/admin/`

**Contact**: support@vatochito.com

---

**Good luck with your launch! 🚀**
