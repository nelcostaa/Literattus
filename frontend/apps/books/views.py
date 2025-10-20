"""
Books views - handles book catalog, search, and details.
Fetches data from FastAPI backend.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests
from django.conf import settings


@login_required
def book_list(request):
    """Display list of books from catalog."""
    # TODO: Fetch from FastAPI backend
    # response = requests.get(f"{settings.FASTAPI_BACKEND_URL}/api/books/")
    context = {
        'title': 'Book Catalog',
    }
    return render(request, 'books/book_list.html', context)


@login_required
def book_detail(request, book_id):
    """Display book details."""
    # TODO: Fetch from FastAPI backend
    # response = requests.get(f"{settings.FASTAPI_BACKEND_URL}/api/books/{book_id}")
    context = {
        'title': 'Book Details',
        'book_id': book_id,
    }
    return render(request, 'books/book_detail.html', context)


@login_required
def book_search(request):
    """Search for books using Google Books API via backend."""
    query = request.GET.get('q', '')
    # TODO: Implement search
    # response = requests.get(f"{settings.FASTAPI_BACKEND_URL}/api/books/search?q={query}")
    context = {
        'title': 'Search Books',
        'query': query,
    }
    return render(request, 'books/book_search.html', context)

