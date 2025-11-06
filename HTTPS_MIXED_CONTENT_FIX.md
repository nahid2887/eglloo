# Mixed Content Error - HTTPS Configuration Guide

## Problem
Your frontend is served over **HTTPS** but is trying to connect to backend over **HTTP**:
- ❌ Frontend: `https://chic-brioche-594496.netlify.app` (HTTPS)
- ❌ Backend: `http://10.10.13.27:8002` (HTTP)

Browsers block this for security reasons.

## Solutions

### Option 1: Deploy Backend with HTTPS (Recommended for Production)

You need to deploy your Django backend to a server with HTTPS support. Here are popular options:

#### A. Using PythonAnywhere (Easy)
1. Go to https://www.pythonanywhere.com
2. Sign up for free account
3. Upload your Django project
4. They provide HTTPS automatically
5. Update frontend to use: `https://yourusername.pythonanywhere.com/api/`

#### B. Using Heroku (No longer free tier, but was popular)
1. Deploy Django app to Heroku
2. Heroku provides free HTTPS
3. Update frontend to use Heroku URL

#### C. Using AWS/DigitalOcean/Linode
1. Deploy Django to cloud server
2. Install SSL certificate (Let's Encrypt - free)
3. Configure nginx/Apache with SSL
4. Update frontend to use HTTPS URL

#### D. Using Render.com (Free tier available)
1. https://render.com
2. Deploy Django app
3. Free HTTPS included
4. Update frontend to use Render URL

### Option 2: Update Frontend to Use HTTPS Backend (Temporary Testing)

If you have a HTTPS backend URL, update your frontend API configuration:

**Current (❌ Wrong):**
```javascript
const API_BASE = 'http://10.10.13.27:8002/api'
```

**Should be (✅ Correct):**
```javascript
const API_BASE = 'https://your-backend-domain.com/api'
```

### Option 3: Serve Django with HTTPS Locally (Advanced)

For local testing with HTTPS, use `runserver_plus` with SSL:

```bash
pip install django-extensions
python manage.py runserver_plus --cert-file cert.crt --key-file key.key
```

---

## HTTPS Configuration in Django Settings

To enable HTTPS support in your backend, add these settings:

```python
# settings.py

# Force HTTPS in production
if not DEBUG:  # Only in production
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Allow your frontend HTTPS domain
CORS_ALLOWED_ORIGINS = [
    "https://chic-brioche-594496.netlify.app",
    "http://localhost:3000",  # for local development
    "http://localhost:8000",  # for local development
]

CSRF_TRUSTED_ORIGINS = [
    "https://chic-brioche-594496.netlify.app",
]
```

---

## Quick Fix: Deploy to Render.com (Free)

### Step 1: Create Render Account
- Go to https://render.com
- Sign up with GitHub

### Step 2: Create requirements.txt
Make sure you have `requirements.txt` in your project root:
```bash
cd /c/eagleeyeau
pip freeze > requirements.txt
```

### Step 3: Create render.yaml
In your project root, create `render.yaml`:
```yaml
services:
  - type: web
    name: eagleeyeau-api
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
    startCommand: gunicorn eagleeyeau.wsgi:application --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10
      - key: DEBUG
        value: false
      - key: SECRET_KEY
        generateValue: true
```

### Step 4: Deploy
1. Push code to GitHub
2. Connect GitHub repo to Render
3. Select branch to deploy
4. Render automatically provides HTTPS URL

### Step 5: Update Frontend
Update your frontend to use the Render HTTPS URL:
```javascript
const API_BASE = 'https://eagleeyeau-api.onrender.com/api'
```

---

## Updated CORS Settings After Deployment

Once your backend has HTTPS, update `settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "https://chic-brioche-594496.netlify.app",  # Your frontend
    "https://eagleeyeau-api.onrender.com",      # Your backend (for OPTIONS preflight)
]

CSRF_TRUSTED_ORIGINS = [
    "https://chic-brioche-594496.netlify.app",
    "https://eagleeyeau-api.onrender.com",
]
```

---

## Environment-Specific Configuration

Update `settings.py` to handle development vs production:

```python
import os
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)

# Development (localhost)
if DEBUG:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '10.10.13.27']
    CORS_ALLOW_ALL_ORIGINS = True
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Production
else:
    ALLOWED_HOSTS = ['your-backend-domain.com']
    CORS_ALLOWED_ORIGINS = [
        'https://chic-brioche-594496.netlify.app',
    ]
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
```

---

## Browser Console Check

Open DevTools (F12) → Console and look for:

✅ **Good:**
```
XMLHttpRequest request to 'https://...' succeeded
```

❌ **Bad:**
```
Mixed Content: The page at 'https://...' was loaded over HTTPS, but requested an insecure resource 'http://...'
```

---

## Recommended Next Steps

1. **For Development (Now):** 
   - Frontend can keep calling `http://10.10.13.27:8002`
   - But this won't work in production

2. **For Production:**
   - Deploy Django backend to Render.com or similar (takes 5 minutes)
   - Get HTTPS URL from provider
   - Update frontend to use HTTPS URL
   - Deploy frontend (already done on Netlify)

---

## Testing with Local HTTPS

To test locally without deploying:

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Run with SSL
pip install django-extensions
python manage.py runserver_plus --cert-file cert.pem --key-file key.key 0.0.0.0:8002

# Update frontend to: https://localhost:8002/api/
# Accept browser's SSL warning
```

---

## Summary

| Scenario | Frontend | Backend | Status |
|----------|----------|---------|--------|
| Local Dev | `http://localhost:3000` | `http://localhost:8000` | ✅ Works |
| Current Prod | `https://netlify...` | `http://10.10.13.27:8002` | ❌ Mixed Content Error |
| Fixed Prod | `https://netlify...` | `https://render.com...` | ✅ Works |

**The fix: Deploy backend to HTTPS provider like Render.com** 🚀
