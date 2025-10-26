"""
Core views for Literattus frontend.
Handles home page, dashboard, and main application pages.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
import requests
from django.conf import settings
from loguru import logger
from .decorators import jwt_login_required


def home(request):
    """Landing page for non-authenticated users."""
    return render(request, 'main/home.html', {
        'title': 'Welcome to Literattus'
    })


@jwt_login_required
def dashboard(request):
    """
    Dashboard view - shows user's reading progress, clubs, and recommendations.
    Fetches data from FastAPI backend.
    """
    # Get user data from session (already loaded during login)
    user_name = request.session.get('user_name', 'User')
    user_email = request.session.get('user_email', '')
    
    context = {
        'title': 'Dashboard',
        'user_name': user_name,
        'user_email': user_email,
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
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email and password are required')
            return render(request, 'auth/login.html', {'title': 'Login'})
        
        try:
            # Call FastAPI login endpoint
            response = requests.post(
                f"{settings.FASTAPI_BACKEND_URL}/api/auth/login",
                json={"email": email, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                access_token = data['access_token']
                
                # Fetch user data using the access token
                try:
                    user_response = requests.get(
                        f"{settings.FASTAPI_BACKEND_URL}/api/auth/me",
                        headers={'Authorization': f'Bearer {access_token}'},
                        timeout=10
                    )
                    
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        
                        # Store token and user info in session
                        request.session['access_token'] = access_token
                        request.session['refresh_token'] = data.get('refresh_token')
                        request.session['user_id'] = user_data['id']
                        request.session['user_email'] = user_data['email']
                        request.session['user_name'] = f"{user_data['firstName']} {user_data['lastName']}"
                        request.session['username'] = user_data.get('username', '')
                        
                        messages.success(request, f'Welcome back, {user_data["firstName"]}!')
                        
                        # Redirect to next page or dashboard
                        next_url = request.GET.get('next', 'core:dashboard')
                        return redirect(next_url)
                    else:
                        logger.error(f"Failed to fetch user data: {user_response.status_code}")
                        messages.error(request, 'Login failed: Unable to fetch user data')
                        
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error fetching user data: {e}")
                    messages.error(request, 'Login failed: Unable to fetch user data')
            else:
                error_msg = 'Invalid email or password'
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
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Basic validation
        errors = []
        if not all([email, username, password, first_name, last_name]):
            errors.append('All fields are required')
        if password != confirm_password:
            errors.append('Passwords do not match')
        if len(password) < 8:
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
                    "password": password,
                    "firstName": first_name,
                    "lastName": last_name
                },
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                messages.success(request, 'Registration successful! Please login.')
                return redirect('core:login')
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
    return redirect('core:home')

