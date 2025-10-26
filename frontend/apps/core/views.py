"""
Core views for Literattus frontend.
Handles home page, dashboard, and main application pages.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
import requests
from django.conf import settings
from loguru import logger


def home(request):
    """Landing page for non-authenticated users."""
    return render(request, 'main/home.html', {
        'title': 'Welcome to Literattus'
    })


@login_required
def dashboard(request):
    """
    Dashboard view - shows user's reading progress, clubs, and recommendations.
    Fetches data from FastAPI backend.
    """
    # TODO: Fetch data from FastAPI backend
    # Example:
    # response = requests.get(f"{settings.FASTAPI_BACKEND_URL}/api/users/me")
    # user_data = response.json()
    
    context = {
        'title': 'Dashboard',
        # Add fetched data here
    }
    return render(request, 'main/dashboard.html', context)


def about(request):
    """About page."""
    return render(request, 'main/about.html', {
        'title': 'About Literattus'
    })


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Handle user login with FastAPI backend.
    Stores JWT token in session.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        REDACTED = request.POST.get('REDACTED')
        
        if not email or not REDACTED:
            messages.error(request, 'Email and REDACTED are required')
            return render(request, 'auth/login.html', {'title': 'Login'})
        
        try:
            # Call FastAPI login endpoint
            response = requests.post(
                f"{settings.FASTAPI_BACKEND_URL}/api/auth/login",
                json={"email": email, "REDACTED": REDACTED},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Store token and user info in session
                request.session['access_token'] = data['access_token']
                request.session['user_id'] = data['user']['id']
                request.session['user_email'] = data['user']['email']
                request.session['user_name'] = f"{data['user']['firstName']} {data['user']['lastName']}"
                
                messages.success(request, 'Successfully logged in!')
                
                # Redirect to next page or dashboard
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                error_msg = 'Invalid email or REDACTED'
                if response.status_code == 422:
                    error_msg = 'Invalid request format'
                messages.error(request, error_msg)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Login request failed: {e}")
            messages.error(request, 'Unable to connect to authentication service')
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            messages.error(request, 'An unexpected error occurred')
    
    return render(request, 'auth/login.html', {'title': 'Login'})


@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    Handle user registration with FastAPI backend.
    """
    if request.method == 'POST':
        # Extract form data
        email = request.POST.get('email')
        username = request.POST.get('username')
        REDACTED = request.POST.get('REDACTED')
        confirm_REDACTED = request.POST.get('confirm_REDACTED')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Basic validation
        errors = []
        if not all([email, username, REDACTED, first_name, last_name]):
            errors.append('All fields are required')
        if REDACTED != confirm_REDACTED:
            errors.append('Passwords do not match')
        if len(REDACTED) < 8:
            errors.append('Password must be at least 8 characters')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'auth/register.html', {
                'title': 'Register',
                'form_data': request.POST
            })
        
        try:
            # Call FastAPI register endpoint
            response = requests.post(
                f"{settings.FASTAPI_BACKEND_URL}/api/auth/register",
                json={
                    "email": email,
                    "username": username,
                    "REDACTED": REDACTED,
                    "firstName": first_name,
                    "lastName": last_name
                },
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                messages.success(request, 'Registration successful! Please login.')
                return redirect('login')
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get('detail', 'Registration failed')
                messages.error(request, error_msg)
            else:
                messages.error(request, 'Registration failed. Please try again.')
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Registration request failed: {e}")
            messages.error(request, 'Unable to connect to registration service')
        except Exception as e:
            logger.error(f"Unexpected error during registration: {e}")
            messages.error(request, 'An unexpected error occurred')
    
    return render(request, 'auth/register.html', {'title': 'Register'})


def logout_view(request):
    """
    Logout user by clearing session.
    """
    # Clear session data
    request.session.flush()
    messages.success(request, 'Successfully logged out')
    return redirect('home')

