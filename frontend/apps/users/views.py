"""
Users views - handles user profiles.
Authentication is handled by core app.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from django.conf import settings
from apps.core.decorators import jwt_login_required


@jwt_login_required
def profile(request):
    """User profile page - displays user information from session."""
    user_name = request.session.get('user_name', 'User')
    user_email = request.session.get('user_email', '')
    username = request.session.get('username', '')
    user_id = request.session.get('user_id', '')
    
    context = {
        'title': 'My Profile',
        'user_name': user_name,
        'user_email': user_email,
        'username': username,
        'user_id': user_id,
    }
    return render(request, 'auth/profile.html', context)

