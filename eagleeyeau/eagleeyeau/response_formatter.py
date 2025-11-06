"""
Custom response formatter to add success field to all API responses
"""
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status


class CustomJSONRenderer(JSONRenderer):
    """
    Custom JSON renderer that wraps all responses with success field
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Handle Response objects by extracting their data
        if isinstance(data, Response):
            data = data.data
        
        # If data already has 'success', 'message' fields (from format_response), use it as-is
        if isinstance(data, dict) and 'success' in data and 'message' in data:
            # Already formatted by format_response
            return super().render(data, accepted_media_type, renderer_context)
        
        # Format the response data for non-formatted responses (e.g., exceptions)
        if renderer_context and renderer_context.get('response'):
            response = renderer_context['response']
            status_code = response.status_code
            
            # Check if it's an error response
            if status_code >= 400:
                # Try to extract meaningful error message
                error_message = 'An error occurred'
                if isinstance(data, dict):
                    if 'detail' in data:
                        error_message = str(data['detail'])
                    elif 'message' in data:
                        error_message = str(data['message'])
                    elif 'error' in data:
                        error_message = str(data['error'])
                    else:
                        # Get first error from any field
                        for key, value in data.items():
                            if isinstance(value, list) and value:
                                error_message = f"{key}: {str(value[0])}"
                            elif value:
                                error_message = f"{key}: {str(value)}"
                            break
                
                formatted_data = {
                    'success': False,
                    'error': True,
                    'status_code': status_code,
                    'message': error_message,
                    'data': data
                }
            else:
                formatted_data = {
                    'success': True,
                    'error': False,
                    'status_code': status_code,
                    'message': 'Success',
                    'data': data
                }
        else:
            # Fallback formatting
            formatted_data = {
                'success': True,
                'error': False,
                'status_code': 200,
                'message': 'Success',
                'data': data
            }
        
        return super().render(formatted_data, accepted_media_type, renderer_context)
    
    def _get_default_message(self, status_code):
        """Get default success message based on status code"""
        messages = {
            200: 'Request successful',
            201: 'Created successfully',
            202: 'Accepted',
            204: 'Deleted successfully',
        }
        return messages.get(status_code, 'Request successful')


def custom_exception_handler(exc, context):
    """
    Custom exception handler that adds success=false to all error responses
    """
    # Call REST framework's default exception handler first
    response = drf_exception_handler(exc, context)

    if response is not None:
        # Extract error message
        error_data = response.data
        error_message = _extract_error_message(error_data, response.status_code)
        
        # Add success=false to error responses
        custom_response_data = {
            'success': False,
            'message': error_message,
            'error': response.data
        }
        response.data = custom_response_data

    return response


def _extract_error_message(error_data, status_code):
    """Extract or generate error message from error data"""
    # Check for common error message fields
    if isinstance(error_data, dict):
        if 'detail' in error_data:
            return str(error_data['detail'])
        if 'message' in error_data:
            return str(error_data['message'])
        if 'error' in error_data:
            return str(error_data['error'])
        # Get first error message from field errors
        for key, value in error_data.items():
            if isinstance(value, list) and value:
                return f"{key}: {str(value[0])}"
            return f"{key}: {str(value)}"
    
    # Default messages based on status code
    default_messages = {
        400: 'Bad request',
        401: 'Authentication required',
        403: 'Permission denied',
        404: 'Resource not found',
        405: 'Method not allowed',
        500: 'Internal server error',
    }
    
    return default_messages.get(status_code, 'Request failed')


def extract_error_message(error_data, status_code=None):
    """Public wrapper for extracting a concise error message.

    If status_code is not provided, try common keys to guess a code (default to 400).
    """
    if status_code is None:
        # default to 400 for serializer validation errors
        status_code = 400
    return _extract_error_message(error_data, status_code)


def format_response(data=None, message=None, status_code=status.HTTP_200_OK, success=True):
    """
    Helper function to format responses consistently with custom messages
    
    Args:
        data: The response data
        message: Custom success/error message
        status_code: HTTP status code (not used when returning dict)
        success: Whether the request was successful
    
    Returns:
        Dictionary with formatted data (can be passed to Response)
    """
    response_data = {
        'success': success,
        'message': message or ('Request successful' if success else 'Request failed'),
    }
    
    if data is not None:
        response_data['data'] = data
    
    return response_data
