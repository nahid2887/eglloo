# CORS Configuration Guide

## What is CORS?
CORS (Cross-Origin Resource Sharing) allows browsers to make requests from one domain to another. Your frontend on Netlify needs to communicate with your Django backend API.

## Current Configuration

### Frontend URL
- **Domain:** `https://chic-brioche-594496.netlify.app`
- **Status:** ✅ Added to CORS_ALLOWED_ORIGINS

### Backend URLs
- `http://localhost:3000` (local frontend dev)
- `http://localhost:8000` (local backend)
- `http://localhost:8080` (alternative local port)
- `https://chic-brioche-594496.netlify.app` (production frontend)

## Settings Applied

### 1. CORS Configuration (settings.py)
```python
CORS_ALLOW_ALL_ORIGINS = False  # Secure - whitelist only needed origins
CORS_ALLOW_CREDENTIALS = True   # Allow cookies and authorization headers
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
    "https://chic-brioche-594496.netlify.app",
    "https://chic-brioche-594496.netlify.app/",
]
```

### 2. CORS Headers Allowed
```python
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',          # JWT tokens
    'content-type',           # JSON
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',           # CSRF token
    'x-requested-with',
]
```

### 3. CSRF Trusted Origins
```python
CSRF_TRUSTED_ORIGINS = [
    "https://chic-brioche-594496.netlify.app",
]
```

### 4. Middleware Order (CRITICAL!)
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # ← Must be near the top
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # ... other middleware
]
```

## How It Works

1. **Browser** sends request from `https://chic-brioche-594496.netlify.app` to Django backend
2. **Django** receives request and checks:
   - Is the Origin in `CORS_ALLOWED_ORIGINS`?
   - Are the request headers in `CORS_ALLOW_HEADERS`?
3. **Django** responds with:
   - `Access-Control-Allow-Origin: https://chic-brioche-594496.netlify.app`
   - `Access-Control-Allow-Credentials: true`
   - `Access-Control-Allow-Headers: authorization, content-type, ...`
4. **Browser** sees the allow headers and permits the response

## Testing CORS

### Using curl
```bash
curl -X GET "http://localhost:8000/api/auth/profile/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Origin: https://chic-brioche-594496.netlify.app" \
  -H "Content-Type: application/json"
```

### Check Response Headers
Look for these headers in the response:
```
Access-Control-Allow-Origin: https://chic-brioche-594496.netlify.app
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
```

## Browser Console Debugging

If you still see CORS errors:

1. **Open DevTools** (F12 → Network tab)
2. **Look for failed requests** (red X)
3. **Click the request** and check "Response Headers"
4. **Look for:**
   - ✅ `Access-Control-Allow-Origin` header exists
   - ✅ Value matches your frontend domain
   - ✅ `Access-Control-Allow-Credentials: true`

### Common CORS Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `No 'Access-Control-Allow-Origin' header` | Domain not whitelisted | Add to `CORS_ALLOWED_ORIGINS` |
| `Credentials mode is 'include' but...` | Credentials not allowed | Set `CORS_ALLOW_CREDENTIALS = True` |
| `Method not allowed` | HTTP method not permitted | Check `CORS_ALLOW_METHODS` |
| `Header not allowed` | Custom header not permitted | Add to `CORS_ALLOW_HEADERS` |

## Adding More Frontend Domains

If you deploy to another domain, add it to `settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    # ... existing origins
    "https://mynewdomain.com",
    "https://mynewdomain.netlify.app",
]

CSRF_TRUSTED_ORIGINS = [
    # ... existing origins
    "https://mynewdomain.com",
    "https://mynewdomain.netlify.app",
]
```

## Production vs Development

### Development (Local Testing)
```python
CORS_ALLOW_ALL_ORIGINS = True  # Accept all origins
```

### Production (Current Setup)
```python
CORS_ALLOW_ALL_ORIGINS = False  # Strict whitelist
CORS_ALLOWED_ORIGINS = [...]    # Only specific domains
```

## Verify Installation

Run in Django shell to verify:
```python
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CORS_ALLOWED_ORIGINS)
>>> print(settings.CORS_ALLOW_CREDENTIALS)
```

## Frontend API Calls

Your frontend should now be able to make requests like:

### JavaScript/Fetch
```javascript
const response = await fetch('http://your-api-domain.com/api/auth/profile/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  credentials: 'include'  // Include cookies if using session auth
});
```

### Axios
```javascript
const instance = axios.create({
  baseURL: 'http://your-api-domain.com/api',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  withCredentials: true  // Include cookies
});
```

## Restart Django

After making changes to `settings.py`, restart the Django server:

```bash
python manage.py runserver
```

The CORS configuration should now be active! 🚀
