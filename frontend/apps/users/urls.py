"""URL configuration for users app - profile and settings only."""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User profile and settings (auth is handled by core app)
    path('profile/', views.profile, name='profile'),
]

