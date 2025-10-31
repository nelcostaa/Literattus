"""
Books views - handles book catalog, search, and details.
Fetches data from FastAPI backend.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
import requests
from django.conf import settings
from loguru import logger
from apps.core.decorators import jwt_login_required


def get_auth_headers(request):
    """Get authorization headers from session."""
    token = request.session.get('access_token')
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}


@jwt_login_required
def book_catalog(request):
    """Display user's saved books from database."""
    try:
        # Fetch books from FastAPI backend
        response = requests.get(
            f"{settings.FASTAPI_BACKEND_URL}/api/books/",
            headers=get_auth_headers(request),
            timeout=10
        )
        
        if response.status_code == 200:
            books = response.json()
        else:
            logger.warning(f"Failed to fetch books: {response.status_code}")
            books = []
            messages.warning(request, 'Unable to load your book catalog')
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching books: {e}")
        books = []
        messages.error(request, 'Unable to connect to book service')
    
    context = {
        'title': 'My Book Catalog',
        'books': books
    }
    return render(request, 'books/catalog.html', context)


@jwt_login_required
def book_search(request):
    """Search for books using Google Books API via backend."""
    books = []
    query = request.GET.get('q', '')
    
    if query:
        try:
            # Search via FastAPI backend
            response = requests.get(
                f"{settings.FASTAPI_BACKEND_URL}/api/books/search",
                params={"q": query, "max_results": 20},
                headers=get_auth_headers(request),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                raw_books = data.get('results', [])
                
                # Transform Google Books API response for easier template access
                books = []
                for item in raw_books:
                    # Case 1: Raw Google Books item structure
                    if item.get('id') and ('volumeInfo' in item):
                        vol_info = item.get('volumeInfo', {})
                        image_links = vol_info.get('imageLinks', {})
                        books.append({
                            'id': item.get('id'),
                            'title': vol_info.get('title', 'Untitled'),
                            'authors': vol_info.get('authors', []),
                            'published_date': vol_info.get('publishedDate', ''),
                            'thumbnail': image_links.get('thumbnail', ''),
                            'description': vol_info.get('description', '')
                        })
                    # Case 2: Backend-parsed item structure
                    elif item.get('googleBooksId'):
                        # item keys: googleBooksId, title, author (string), coverImage, publishedDate, pageCount, averageRating
                        author_str = item.get('author') or ''
                        authors_list = [a.strip() for a in author_str.split(',') if a.strip()] if author_str else []
                        books.append({
                            'id': item.get('googleBooksId'),
                            'title': item.get('title', 'Untitled'),
                            'authors': authors_list,
                            'published_date': item.get('publishedDate', ''),
                            'thumbnail': item.get('coverImage', ''),
                            'description': item.get('description', '')
                        })
                    # Ignore items without identifiers
                    else:
                        continue
                
                if not books and query:
                    messages.info(request, f'No valid books found for "{query}"')
                elif books:
                    logger.info(f"Search successful: {len(books)} books found")
                    logger.debug(f"First book: {books[0] if books else 'None'}")
            else:
                logger.warning(f"Search failed: {response.status_code}")
                messages.warning(request, 'Search service temporarily unavailable')
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Search error: {e}")
            messages.error(request, 'Unable to search books at this time')
        except Exception as e:
            logger.error(f"Unexpected error in search: {e}")
            messages.error(request, 'An unexpected error occurred')
    
    context = {
        'title': 'Search Books',
        'query': query,
        'books': books
    }
    logger.info(f"Rendering search template with {len(books)} books")
    return render(request, 'books/search.html', context)


@jwt_login_required
@require_http_methods(["POST"])
def add_book(request, google_book_id):
    """Add book from Google Books to user's catalog."""
    try:
        # Call FastAPI to save book
        response = requests.post(
            f"{settings.FASTAPI_BACKEND_URL}/api/books/search-and-save/{google_book_id}",
            headers=get_auth_headers(request),
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            book_data = response.json()
            messages.success(request, f'Added "{book_data.get("title")}" to your catalog!')
            return redirect('books:catalog')
        elif response.status_code == 404:
            messages.error(request, 'Book not found')
        else:
            messages.error(request, 'Unable to add book to catalog')
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error adding book {google_book_id}: {e}")
        messages.error(request, 'Unable to connect to book service')
    
    # Redirect back to search on error
    return redirect('books:search')


@jwt_login_required
def book_detail(request, book_id):
    """Display detailed information about a book."""
    book = None
    
    try:
        # Fetch book details from FastAPI
        response = requests.get(
            f"{settings.FASTAPI_BACKEND_URL}/api/books/{book_id}",
            headers=get_auth_headers(request),
            timeout=10
        )
        
        if response.status_code == 200:
            book = response.json()
        elif response.status_code == 404:
            messages.error(request, 'Book not found')
            return redirect('books:catalog')
        else:
            messages.warning(request, 'Unable to load book details')
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching book {book_id}: {e}")
        messages.error(request, 'Unable to connect to book service')
        return redirect('books:catalog')
    
    context = {
        'title': book.get('title', 'Book Details') if book else 'Book Details',
        'book': book
    }
    return render(request, 'books/detail.html', context)


# Keep old views for backward compatibility (redirects)
@jwt_login_required
def book_list(request):
    """Legacy redirect to catalog."""
    return redirect('books:catalog')