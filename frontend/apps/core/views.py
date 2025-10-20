"""
Core views for Literattus frontend.
Handles home page, dashboard, and main application pages.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests
from django.conf import settings


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

