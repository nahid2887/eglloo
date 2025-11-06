# Quick Fix: Mixed Content Error

## The Problem
```
Mixed Content: The page at 'https://chic-brioche-594496.netlify.app/' 
was loaded over HTTPS, but requested an insecure resource 'http://10.10.13.27:8002/api/auth/login/'. 
This request has been blocked.
```

## Why This Happens
- Frontend (Netlify) = **HTTPS** ✅
- Backend (Your server) = **HTTP** ❌
- Browsers block this for security

## Quick Solutions

### For Development (Temporary)
If you want to test locally, use insecure HTTPS bypass:

**Frontend (React/Vue):**
```javascript
// Only for development/testing!
// This suppresses the security warning
const API_URL = 'http://10.10.13.27:8002/api'

// Make sure CORS is enabled on backend
// See CORS_CONFIGURATION_GUIDE.md
```

### For Production (Recommended)
Deploy backend to HTTPS provider (2 options):

#### Option A: Render.com (5 minutes)
1. Push code to GitHub
2. Deploy at render.com
3. Get HTTPS URL automatically
4. Update frontend to use HTTPS URL
5. Done!
→ See `RENDER_DEPLOYMENT_GUIDE.md`

#### Option B: Your Server (Advanced)
Add SSL certificate to `10.10.13.27`:
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Run Django with HTTPS
python manage.py runserver_plus --cert-file /path/to/cert.pem --key-file /path/to/key.pem
```

## Frontend Configuration Changes

### Before (❌ Wrong)
```javascript
const API = 'http://10.10.13.27:8002/api'
```

### After (✅ Correct)
```javascript
// Option 1: Direct HTTPS URL
const API = 'https://eagleeyeau-api.onrender.com/api'

// Option 2: Environment variable
const API = process.env.VITE_API_URL || 'https://eagleeyeau-api.onrender.com/api'
```

## Backend Settings (Already Updated)

✅ Your `settings.py` now has:
```python
# Production HTTPS
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

✅ CORS configured for Netlify frontend

## Next Steps

**Recommended:** Deploy to Render.com (2-5 minutes)
1. See `RENDER_DEPLOYMENT_GUIDE.md`
2. Get HTTPS URL
3. Update frontend
4. Done!

**Alternative:** Use local HTTPS for testing
1. Generate SSL certificate
2. Run Django with SSL
3. Test locally

## Verify It Works

### Check 1: Browser Console
Open DevTools (F12) → Console
- ❌ Error: "Mixed Content... was blocked"
- ✅ No error, API calls succeed

### Check 2: Network Tab
Open DevTools (F12) → Network
- ❌ Red X on API requests
- ✅ Green checkmark, Status 200

### Check 3: Response Headers
Click API request → Response Headers
- ✅ `Access-Control-Allow-Origin: https://chic-brioche-594496.netlify.app`
- ✅ `Access-Control-Allow-Credentials: true`

## Timeline

- **Now:** Your backend runs on HTTP (development only)
- **This is why:** Netlify frontend (HTTPS) can't call it
- **Solution:** Deploy backend to HTTPS provider
- **Time to fix:** ~5 minutes with Render.com

Your Django server is running on port 8002 and is ready! You just need to deploy it to a service that provides HTTPS. 🚀
