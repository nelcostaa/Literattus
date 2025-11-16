"""
Custom middleware for Literattus frontend.
"""

from django.http import HttpResponse
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


class HealthCheckMiddleware:
    """
    Middleware to handle health check endpoint without redirects.
    Prevents APPEND_SLASH and SECURE_SSL_REDIRECT from redirecting health checks.
    Must be placed BEFORE SecurityMiddleware and CommonMiddleware.
    
    This middleware intercepts health check requests BEFORE any other middleware
    can process them, ensuring no redirects occur.
    """
    
    HEALTH_CHECK_PATHS = ['/health', '/health/', '/healthz', '/healthz/']
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if this is a health check request
        # This MUST be checked FIRST, before any other middleware runs
        if request.path in self.HEALTH_CHECK_PATHS:
            # Log for debugging - this will help us verify the middleware is running
            try:
                logger.info(
                    f"HealthCheckMiddleware: Intercepted {request.path} "
                    f"from {request.META.get('REMOTE_ADDR', 'unknown')} "
                    f"scheme={request.scheme} is_secure={request.is_secure()}"
                )
            except Exception:
                # If logging fails, continue anyway
                pass
            
            # Return 200 OK immediately, bypassing ALL other middleware
            # This response is returned BEFORE SecurityMiddleware can redirect
            response = HttpResponse(
                json.dumps({'status': 'healthy', 'path': request.path}),
                content_type='application/json',
                status=200
            )
            # Explicitly ensure no redirect headers can be added
            # Use delattr to remove Location header if it exists
            if hasattr(response, '_headers'):
                # Django < 3.2
                if 'location' in response._headers:
                    del response._headers['location']
                if 'Location' in response._headers:
                    del response._headers['Location']
            else:
                # Django >= 3.2 uses response.headers (case-insensitive dict)
                response.headers.pop('Location', None)
                response.headers.pop('location', None)
            return response
        
        # For non-health-check requests, continue with normal middleware chain
        return self.get_response(request)

