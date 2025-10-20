"""
Clubs views - handles book club pages and management.
Fetches data from FastAPI backend.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def club_list(request):
    """Display list of book clubs."""
    # TODO: Fetch from FastAPI backend
    context = {
        'title': 'Book Clubs',
    }
    return render(request, 'clubs/club_list.html', context)


@login_required
def club_detail(request, club_id):
    """Display club details and members."""
    # TODO: Fetch from FastAPI backend
    context = {
        'title': 'Club Details',
        'club_id': club_id,
    }
    return render(request, 'clubs/club_detail.html', context)


@login_required
def my_clubs(request):
    """Display user's clubs."""
    # TODO: Fetch from FastAPI backend
    context = {
        'title': 'My Clubs',
    }
    return render(request, 'clubs/my_clubs.html', context)

