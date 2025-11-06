# Deploy Django Backend to Render.com - Step by Step Guide

## What is Render?
Render.com is a cloud platform that automatically deploys your Django app and provides HTTPS. This solves your Mixed Content error!

## Prerequisites
- GitHub account (free at github.com)
- Render account (free tier available)

## Step 1: Prepare Your Django Project

### 1.1 Create requirements.txt
```bash
cd /c/eagleeyeau
pip freeze > requirements.txt
```

Check that `requirements.txt` contains:
```
Django==5.2.7
djangorestframework
django-cors-headers
djangorestframework-simplejwt
# ... other packages
```

### 1.2 Create .env file for production variables
Create `c:\eagleeyeau\eagleeyeau\.env`:
```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.onrender.com
DATABASE_URL=your-database-url
EMAIL_HOST=smtp.strato.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@wiiz.ai
EMAIL_HOST_PASSWORD=your-password
```

### 1.3 Update settings.py for database
Add to `settings.py`:
```python
import dj_database_url

if not DEBUG:
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL'),
            conn_max_age=600
        )
    }
```

## Step 2: Push to GitHub

### 2.1 Initialize Git (if not already done)
```bash
cd /c/eagleeyeau
git init
git add .
git commit -m "Initial commit for Render deployment"
```

### 2.2 Create GitHub repository
1. Go to https://github.com/new
2. Create repository: `eagleeyeau-api` or similar
3. Copy the commands and push:
```bash
git remote add origin https://github.com/YOUR_USERNAME/eagleeyeau-api.git
git branch -M main
git push -u origin main
```

## Step 3: Create render.yaml Configuration

Create `c:\eagleeyeau\render.yaml`:
```yaml
services:
  - type: web
    name: eagleeyeau-api
    env: python
    plan: free
    buildCommand: >
      pip install -r requirements.txt &&
      python eagleeyeau/manage.py migrate &&
      python eagleeyeau/manage.py collectstatic --noinput
    startCommand: gunicorn eagleeyeau.wsgi:application --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10
      - key: DEBUG
        value: false
```

Push to GitHub:
```bash
git add render.yaml
git commit -m "Add Render deployment configuration"
git push
```

## Step 4: Create Render Account and Deploy

### 4.1 Sign up for Render
1. Go to https://render.com
2. Click "Sign up"
3. Choose "GitHub" as sign-up method
4. Authorize Render to access your GitHub

### 4.2 Deploy your app
1. Click "New +" button
2. Select "Web Service"
3. Connect your GitHub repository: `eagleeyeau-api`
4. Configure:
   - **Name:** `eagleeyeau-api`
   - **Environment:** `Python`
   - **Build Command:** Leave empty (uses render.yaml)
   - **Start Command:** Leave empty (uses render.yaml)
   - **Plan:** Free
5. Click "Create Web Service"

### 4.3 Add Environment Variables
1. Go to your service dashboard
2. Click "Environment" tab
3. Add these variables:
   ```
   DEBUG = false
   SECRET_KEY = (generate random string)
   ALLOWED_HOSTS = your-service-name.onrender.com
   DATABASE_URL = (if using external database)
   CORS_ALLOWED_ORIGINS = ["https://chic-brioche-594496.netlify.app"]
   ```
4. Click "Save"

## Step 5: Update Frontend Configuration

Once deployment is complete, Render will show your URL like:
```
https://eagleeyeau-api.onrender.com
```

Update your frontend code to use this HTTPS URL:

**In your frontend project:**
```javascript
// config.js or .env
const API_BASE_URL = 'https://eagleeyeau-api.onrender.com/api'

// Or if using .env:
VITE_API_URL=https://eagleeyeau-api.onrender.com/api
```

## Step 6: Update Django Settings for Production

Update `c:\eagleeyeau\eagleeyeau\eagleeyeau\settings.py`:

```python
# Add Render domain to ALLOWED_HOSTS
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '10.10.13.27',
    'eagleeyeau-api.onrender.com',  # Your Render domain
]

# CORS Configuration for production
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'https://chic-brioche-594496.netlify.app',
    'https://eagleeyeau-api.onrender.com',  # Your backend
]

CSRF_TRUSTED_ORIGINS = [
    'https://chic-brioche-594496.netlify.app',
    'https://eagleeyeau-api.onrender.com',
]
```

Commit and push:
```bash
git add .
git commit -m "Update settings for Render deployment"
git push
```

Render will automatically redeploy!

## Step 7: Verify Everything Works

### 7.1 Test API endpoints
```bash
curl -X GET "https://eagleeyeau-api.onrender.com/api/auth/login/" \
  -H "Content-Type: application/json"
```

### 7.2 Check frontend logs
1. Open DevTools (F12) → Console
2. Should see successful API calls (no Mixed Content errors)
3. Look for: `XMLHttpRequest request to 'https://eagleeyeau-api.onrender.com/api/...' succeeded`

### 7.3 Check Render logs
1. Go to Render dashboard
2. Select your service
3. Click "Logs" tab
4. Check for errors

## Troubleshooting

### "Mixed Content" still showing
- Make sure frontend is calling `https://` (not `http://`)
- Check frontend's config/env file has correct URL
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+F5)

### 502 Bad Gateway
- Check Render logs for errors
- Make sure `gunicorn` is installed: add to `requirements.txt`
- Verify `settings.py` is correct

### Database migrations failed
- Make sure `manage.py` path is correct in buildCommand
- Check database URL in environment variables
- Try: `python eagleeyeau/manage.py migrate --run-syncdb`

### "ModuleNotFoundError"
- Check `requirements.txt` has all packages
- Run `pip freeze > requirements.txt` to update

## Automatic Redeployment

Any push to GitHub will automatically redeploy:

```bash
# Make changes locally
git add .
git commit -m "Your message"
git push

# Render automatically redeploys!
# Check logs at render.com dashboard
```

## Summary

| Before | After |
|--------|-------|
| Frontend: `https://chic-brioche-594496.netlify.app` | ✅ Same |
| Backend: `http://10.10.13.27:8002` | ✅ `https://eagleeyeau-api.onrender.com` |
| CORS Error: ❌ Mixed Content | ✅ No error! |

Your app is now deployed! 🚀
