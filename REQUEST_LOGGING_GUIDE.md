# Django Server Logs - Understanding & Capturing Request Data

## What the Log Line Means

```
[07/Nov/2025 12:08:34] "PATCH /api/admin/estimate-defaults/23/ HTTP/1.1" 200 695
```

### Breakdown:
- **[07/Nov/2025 12:08:34]** - Timestamp when request was processed
- **"PATCH"** - HTTP method used
- **/api/admin/estimate-defaults/23/** - API endpoint called with ID 23
- **HTTP/1.1** - HTTP protocol version
- **200** - HTTP status code (200 = Success)
- **695** - Response size in bytes

---

## How to Get More Detailed Information

### Option 1: Django Logging Configuration (Recommended)

Add this to your `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'verbose',
        },
        'request': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'requests.log',
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['request', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### Option 2: Create Custom Request Logging Middleware

Create a new file: `eagleeyeau/middleware.py`

```python
import json
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Log incoming request
        logger.info(
            f"[REQUEST] {request.method} {request.path} "
            f"| User: {request.user} "
            f"| IP: {self.get_client_ip(request)}"
        )
        return None

    def process_response(self, request, response):
        # Log response details
        logger.info(
            f"[RESPONSE] {request.method} {request.path} "
            f"| Status: {response.status_code} "
            f"| Size: {len(response.content)} bytes"
        )
        return response

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

Add to `settings.py` MIDDLEWARE:

```python
MIDDLEWARE = [
    # ... existing middleware ...
    'eagleeyeau.middleware.RequestLoggingMiddleware',
]
```

### Option 3: Use Django Debug Toolbar (For Development)

```bash
pip install django-debug-toolbar
```

Add to `settings.py`:

```python
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

Add to `urls.py`:

```python
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```

---

## What Data You Can Capture

### Request Information:
- **Method**: GET, POST, PATCH, DELETE, etc.
- **Path**: /api/endpoint/
- **Query Parameters**: ?search=value&page=1
- **Request Body**: JSON payload sent
- **Headers**: Authorization, Content-Type, etc.
- **User**: Which user made the request
- **IP Address**: Client's IP address
- **Timestamp**: When request was received

### Response Information:
- **Status Code**: 200, 404, 500, etc.
- **Response Size**: Bytes returned
- **Response Time**: How long it took
- **Headers**: Set-Cookie, Content-Type, etc.
- **Response Body**: JSON response sent

### Database Information:
- **Queries**: SQL queries executed
- **Query Count**: How many queries ran
- **Query Time**: Total database time

---

## Example Output with Custom Logging

```
[DEBUG] 07/Nov/2025 12:08:34 middleware 1234 5678
[REQUEST] PATCH /api/admin/estimate-defaults/23/ 
| User: nahid2887 
| IP: 192.168.1.100

[DEBUG] 07/Nov/2025 12:08:34 middleware 1234 5678
[RESPONSE] PATCH /api/admin/estimate-defaults/23/ 
| Status: 200 
| Size: 695 bytes
```

---

## Live Monitoring Commands

### Option A: Tail Django Log File
```bash
tail -f django.log
```

### Option B: Tail Request Log Only
```bash
tail -f requests.log
```

### Option C: Follow with Timestamps
```bash
tail -f django.log | grep -E "(PATCH|POST|GET|DELETE)"
```

### Option D: Search for Specific Endpoint
```bash
tail -f requests.log | grep "estimate-defaults"
```

### Option E: Monitor in Real-time (All logs)
```bash
watch -n 1 'tail -20 django.log'
```

---

## Quick Implementation

### 1. Add to settings.py:

```python
# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django.request': {
            'level': 'DEBUG',
        },
    },
}
```

### 2. Run server with verbose output:
```bash
python manage.py runserver 0.0.0.0:8002 --verbosity 3
```

### 3. Check logs in terminal:
All requests/responses will now show in terminal

---

## Recommended Setup

For your Django project, I recommend:

1. **Development**: Use Django Debug Toolbar (easiest)
2. **Production**: Use structured logging to files
3. **Monitoring**: Use middleware for custom logging

This will give you complete visibility into all API requests and responses! 🚀
