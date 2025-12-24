import json
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all HTTP requests and responses with detailed information.
    """
    
    def process_request(self, request):
        """Log incoming request details"""
        # Get request data
        method = request.method
        path = request.path
        user = request.user if request.user.is_authenticated else "Anonymous"
        ip = self.get_client_ip(request)
        
        # Get query parameters
        query_params = dict(request.GET)
        
        # Log the request
        log_message = (
            f"\n{'='*80}\n"
            f"📨 INCOMING REQUEST\n"
            f"{'='*80}\n"
            f"Time: {self._get_timestamp()}\n"
            f"Method: {method}\n"
            f"Path: {path}\n"
            f"User: {user}\n"
            f"IP Address: {ip}\n"
        )
        
        if query_params:
            log_message += f"Query Params: {query_params}\n"
        
        if request.body and method in ['POST', 'PUT', 'PATCH']:
            try:
                body = json.loads(request.body)
                log_message += f"Body: {json.dumps(body, indent=2)}\n"
            except:
                log_message += f"Body: {request.body[:500]}\n"  # First 500 chars
        
        log_message += f"{'='*80}"
        logger.info(log_message)
        
        # Store request start time for response logging
        request._start_time = __import__('time').time()
        
        return None

    def process_response(self, request, response):
        """Log outgoing response details"""
        # Calculate response time
        if hasattr(request, '_start_time'):
            response_time = __import__('time').time() - request._start_time
        else:
            response_time = 0
        
        # Get response data
        method = request.method
        path = request.path
        status_code = response.status_code
        content_length = len(response.content)
        user = request.user if request.user.is_authenticated else "Anonymous"
        
        # Determine status color/indicator
        if status_code < 300:
            status_indicator = "✅"
        elif status_code < 400:
            status_indicator = "ℹ️"
        elif status_code < 500:
            status_indicator = "⚠️"
        else:
            status_indicator = "❌"
        
        # Log the response
        log_message = (
            f"\n{'='*80}\n"
            f"📤 OUTGOING RESPONSE\n"
            f"{'='*80}\n"
            f"Status: {status_indicator} {status_code}\n"
            f"Method: {method}\n"
            f"Path: {path}\n"
            f"User: {user}\n"
            f"Response Size: {content_length} bytes\n"
            f"Response Time: {response_time:.3f}s\n"
        )
        
        # Log response headers
        log_message += f"\nHeaders:\n"
        for key, value in dict(response.items()).items():
            if key not in ['Set-Cookie']:  # Don't log sensitive headers
                log_message += f"  {key}: {value}\n"
        
        # Try to log response body if JSON
        if 'application/json' in response.get('Content-Type', ''):
            try:
                body = json.loads(response.content)
                log_message += f"\nResponse Body:\n{json.dumps(body, indent=2)}\n"
            except:
                log_message += f"\nResponse Body (raw): {response.content[:500]}\n"
        
        log_message += f"{'='*80}"
        logger.info(log_message)
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def _get_timestamp():
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime('%d/%b/%Y %H:%M:%S')
