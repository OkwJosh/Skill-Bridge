"""
Custom Exception Handler for Standard API Envelope
===================================================

All SkillBridge API responses MUST follow this exact JSON structure:
{
    "status": "success" | "error",
    "data": {},
    "meta": {},
    "errors": []
}

This module intercepts all DRF exceptions and formats them consistently.
"""

from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from django.http import Http404


def standard_exception_handler(exc, context):
    """
    Custom DRF exception handler that formats ALL errors into the standard envelope.
    
    This is set in settings.py:
        REST_FRAMEWORK = {
            'EXCEPTION_HANDLER': 'core.exceptions.standard_exception_handler',
        }
    
    Args:
        exc: The exception that was raised
        context: Dict containing 'view', 'args', 'kwargs', 'request'
    
    Returns:
        Response with standardized error format, or None for unhandled exceptions
    """
    # Get the standard DRF response (or None for non-DRF exceptions)
    response = exception_handler(exc, context)
    
    if response is not None:
        # Extract and format the errors
        errors = _format_errors(response.data, exc)
        
        # Build the standardized error response
        response.data = {
            'status': 'error',
            'data': None,
            'meta': {
                'http_status': response.status_code,
                'error_type': exc.__class__.__name__,
            },
            'errors': errors,
        }
    
    return response


def _format_errors(raw_data, exc) -> list:
    """
    Convert DRF's various error formats into a consistent list of error objects.
    
    DRF returns errors in different formats:
    - {"detail": "message"}                    # Single error
    - {"field": ["error1", "error2"]}          # Field validation errors
    - {"non_field_errors": ["error"]}          # Form-level errors
    - ["error1", "error2"]                     # List of errors
    
    We normalize all of these into:
    [
        {"field": "field_name" | null, "message": "...", "code": "..."},
        ...
    ]
    
    Args:
        raw_data: The raw error data from DRF
        exc: The original exception
    
    Returns:
        List of error dictionaries
    """
    errors = []
    error_code = getattr(exc, 'default_code', 'error')
    
    if isinstance(raw_data, dict):
        for field, messages in raw_data.items():
            # Handle the special "detail" key (single error message)
            if field == 'detail':
                errors.append({
                    'field': None,
                    'message': str(messages),
                    'code': error_code,
                })
            # Handle list of messages for a field
            elif isinstance(messages, list):
                for message in messages:
                    # Handle nested error objects
                    if isinstance(message, dict):
                        errors.append({
                            'field': field,
                            'message': str(message),
                            'code': 'validation_error',
                        })
                    else:
                        errors.append({
                            'field': field if field != 'non_field_errors' else None,
                            'message': str(message),
                            'code': 'validation_error',
                        })
            # Handle single message for a field
            else:
                errors.append({
                    'field': field if field != 'non_field_errors' else None,
                    'message': str(messages),
                    'code': 'validation_error',
                })
    
    elif isinstance(raw_data, list):
        # List of error messages
        for message in raw_data:
            errors.append({
                'field': None,
                'message': str(message),
                'code': error_code,
            })
    
    else:
        # Single error message
        errors.append({
            'field': None,
            'message': str(raw_data),
            'code': error_code,
        })
    
    return errors


# =============================================================================
# CUSTOM EXCEPTIONS (Optional - for cleaner error handling in views)
# =============================================================================

from rest_framework.exceptions import APIException


class BadRequest(APIException):
    """400 Bad Request - Client sent invalid data."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bad request.'
    default_code = 'bad_request'


class NotFound(APIException):
    """404 Not Found - Resource doesn't exist."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Not found.'
    default_code = 'not_found'


class Forbidden(APIException):
    """403 Forbidden - User lacks permission."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'forbidden'


class Conflict(APIException):
    """409 Conflict - Resource already exists or state conflict."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Resource conflict.'
    default_code = 'conflict'
