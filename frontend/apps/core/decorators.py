"""
Custom authentication decorators for JWT-based authentication.
Replaces Django's @login_required for use with FastAPI backend.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def jwt_login_required(function):
    """
    Decorator for views that require JWT authentication via session.
    
    Checks if user has a valid access_token in their session.
    If not, redirects to login page with 'next' parameter.
    
    Usage:
        @jwt_login_required
        def my_view(request):
            # Access token available at: request.session['access_token']
            pass
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        # Check if access token exists in session
        access_token = request.session.get('access_token')
        
        if not access_token:
            # Store the current path to redirect after login
            messages.info(request, 'Please login to access this page')
            next_url = request.get_full_path()
            return redirect(f'/login/?next={next_url}')
        
        # Token exists, allow access
        return function(request, *args, **kwargs)
    
    return wrap

