"""
Utility functions for core app.
Shared helpers for API communication and common operations.
"""

from django.conf import settings


def get_backend_url() -> str:
    """
    Get backend URL, ensuring HTTP (not HTTPS) since ALB is configured for HTTP.
    
    This prevents connection issues when the ALB only has HTTP listeners.
    When HTTPS is configured on the ALB, this function can be updated to support both.
    
    Returns:
        str: Backend URL with HTTP protocol guaranteed
    """
    url = settings.FASTAPI_BACKEND_URL
    # Force HTTP to prevent HTTPS redirect issues
    return url.replace('https://', 'http://')

