"""
Custom JSON Renderer for Standard API Envelope
===============================================

Wraps ALL successful API responses in the standard envelope:
{
    "status": "success",
    "data": <actual_response_data>,
    "meta": {},
    "errors": []
}

Error responses are handled by the exception handler (core/exceptions.py).
"""

from rest_framework.renderers import JSONRenderer


class StandardJSONRenderer(JSONRenderer):
    """
    Custom DRF renderer that wraps all responses in the standard API envelope.
    
    This is set in settings.py:
        REST_FRAMEWORK = {
            'DEFAULT_RENDERER_CLASSES': [
                'core.renderers.StandardJSONRenderer',
            ],
        }
    
    The envelope format:
        Success: {"status": "success", "data": {...}, "meta": {}, "errors": []}
        Error:   {"status": "error", "data": null, "meta": {...}, "errors": [...]}
    """
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render the response data into the standard JSON envelope.
        
        Args:
            data: The response data to render
            accepted_media_type: The accepted media type (application/json)
            renderer_context: Context dict with 'request', 'response', 'view'
        
        Returns:
            JSON string in the standard envelope format
        """
        response = renderer_context.get('response') if renderer_context else None
        
        # Check if this response is already wrapped (from exception handler)
        if self._is_already_wrapped(data):
            return super().render(data, accepted_media_type, renderer_context)
        
        # Check if this is an error response (status >= 400)
        # These should be handled by the exception handler, but just in case
        if response and response.status_code >= 400:
            return super().render(data, accepted_media_type, renderer_context)
        
        # Wrap successful response in standard envelope
        envelope = {
            'status': 'success',
            'data': data,
            'meta': self._build_meta(renderer_context),
            'errors': [],
        }
        
        return super().render(envelope, accepted_media_type, renderer_context)
    
    def _is_already_wrapped(self, data) -> bool:
        """
        Check if the response data is already in envelope format.
        
        This prevents double-wrapping from the exception handler.
        
        Args:
            data: The response data
        
        Returns:
            True if data is already in envelope format
        """
        if not isinstance(data, dict):
            return False
        
        # Check for envelope keys
        return (
            'status' in data and
            'errors' in data and
            data.get('status') in ('success', 'error')
        )
    
    def _build_meta(self, renderer_context) -> dict:
        """
        Build the meta object with pagination and request info.
        
        Args:
            renderer_context: The renderer context with request/response/view
        
        Returns:
            Dictionary with meta information
        """
        meta = {}
        
        if not renderer_context:
            return meta
        
        view = renderer_context.get('view')
        request = renderer_context.get('request')
        
        # Add pagination info if this is a paginated response
        if view and hasattr(view, 'paginator') and view.paginator:
            page = getattr(view.paginator, 'page', None)
            if page:
                meta['pagination'] = {
                    'count': page.paginator.count,
                    'page_size': view.paginator.get_page_size(request),
                    'current_page': page.number,
                    'total_pages': page.paginator.num_pages,
                    'has_next': page.has_next(),
                    'has_previous': page.has_previous(),
                }
        
        return meta
