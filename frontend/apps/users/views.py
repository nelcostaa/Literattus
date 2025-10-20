"""
Users views - handles authentication and user profiles.
Communicates with FastAPI backend for authentication.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
import requests
from django.conf import settings


def login_view(request):
    """User login page."""
    if request.method == 'POST':
        # TODO: Authenticate via FastAPI backend
        # response = requests.post(f"{settings.FASTAPI_BACKEND_URL}/api/auth/login", ...)
        pass
    
    return render(request, 'auth/login.html', {
        'title': 'Login'
    })


def register_view(request):
    """User registration page."""
    if request.method == 'POST':
        # TODO: Register via FastAPI backend
        # response = requests.post(f"{settings.FASTAPI_BACKEND_URL}/api/auth/register", ...)
        pass
    
    return render(request, 'auth/register.html', {
        'title': 'Register'
    })


def logout_view(request):
    """User logout."""
    logout(request)
    return redirect('core:home')


@login_required
def profile(request):
    """User profile page."""
    # TODO: Fetch from FastAPI backend
    context = {
        'title': 'My Profile',
    }
    return render(request, 'auth/profile.html', context)

