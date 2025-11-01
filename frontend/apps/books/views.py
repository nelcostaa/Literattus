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
    """Display user's personal book catalog with reading progress."""
    try:
        # Fetch user's catalog with reading progress from FastAPI backend
        response = requests.get(
            f"{settings.FASTAPI_BACKEND_URL}/api/books/my-catalog",
            headers=get_auth_headers(request),
            timeout=10
        )
        
        if response.status_code == 200:
            books = response.json()
        else:
            logger.warning(f"Failed to fetch catalog: {response.status_code}")
            books = []
            messages.warning(request, 'Unable to load your book catalog')
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching catalog: {e}")
        books = []
        messages.error(request, 'Unable to connect to book service')
    
    # Compute reading statistics
    reading_count = sum(1 for book in books if book.get('status') == 'reading')
    not_started_count = sum(1 for book in books if book.get('status') == 'not_started')
    completed_count = sum(1 for book in books if book.get('status') == 'completed')
    abandoned_count = sum(1 for book in books if book.get('status') == 'abandoned')
    
    context = {
        'title': 'My Book Catalog',
        'books': books,
        'reading_count': reading_count,
        'not_started_count': not_started_count,
        'completed_count': completed_count,
        'abandoned_count': abandoned_count,
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
    """
    Display detailed information about a book.
    Fetches book details, reading progress, user's clubs, and related books.
    """
    book = None
    in_catalog = False
    reading_progress = None
    user_clubs = []
    related_books = []
    
    headers = get_auth_headers(request)
    
    try:
        # 1. Fetch book details from FastAPI (DB)
        response = requests.get(
            f"{settings.FASTAPI_BACKEND_URL}/api/books/{book_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            book = response.json()
            in_catalog = True
        elif response.status_code == 404:
            # Fallback: fetch from Google Books via backend
            fallback = requests.get(
                f"{settings.FASTAPI_BACKEND_URL}/api/books/google/{book_id}",
                headers=headers,
                timeout=10
            )
            if fallback.status_code == 200:
                book = fallback.json()
                in_catalog = False
            else:
                messages.error(request, 'Book not found')
                return redirect('books:catalog')
        else:
            messages.warning(request, 'Unable to load book details')
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching book {book_id}: {e}")
        messages.error(request, 'Unable to connect to book service')
        return redirect('books:catalog')
    
    # 2. Fetch reading progress if book is in catalog
    if in_catalog:
        try:
            progress_response = requests.get(
                f"{settings.FASTAPI_BACKEND_URL}/api/progress/{book_id}",
                headers=headers,
                timeout=10
            )
            if progress_response.status_code == 200:
                reading_progress = progress_response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not fetch reading progress: {e}")
    
    # 3. Fetch user's clubs for "Add to Club" functionality
    try:
        clubs_response = requests.get(
            f"{settings.FASTAPI_BACKEND_URL}/api/clubs/my-clubs",
            headers=headers,
            timeout=10
        )
        if clubs_response.status_code == 200:
            user_clubs = clubs_response.json()
    except requests.exceptions.RequestException as e:
        logger.warning(f"Could not fetch user clubs: {e}")
    
    # 4. Fetch related books
    try:
        related_response = requests.get(
            f"{settings.FASTAPI_BACKEND_URL}/api/books/{book_id}/related",
            headers=headers,
            params={'max_results': 6},
            timeout=10
        )
        if related_response.status_code == 200:
            related_data = related_response.json()
            related_books = related_data.get('results', [])
    except requests.exceptions.RequestException as e:
        logger.warning(f"Could not fetch related books: {e}")
    
    # Calculate reading statistics if progress exists
    reading_stats = None
    if reading_progress and book and book.get('pageCount'):
        total_pages = book.get('pageCount', 0)
        current_page = reading_progress.get('currentPage', 0)
        pages_left = max(0, total_pages - current_page)
        
        # Calculate pages per day if started
        if reading_progress.get('startedAt'):
            from datetime import datetime, timedelta
            try:
                started_at = datetime.fromisoformat(reading_progress['startedAt'].replace('Z', '+00:00'))
                days_elapsed = max(1, (datetime.now(started_at.tzinfo) - started_at).days)
                pages_per_day = current_page / days_elapsed if days_elapsed > 0 else 0
                
                # Estimate completion date
                if pages_per_day > 0 and pages_left > 0:
                    days_remaining = pages_left / pages_per_day
                    estimated_completion = datetime.now() + timedelta(days=int(days_remaining))
                    reading_stats = {
                        'pages_per_day': round(pages_per_day, 1),
                        'days_remaining': round(days_remaining, 0),
                        'estimated_completion': estimated_completion.strftime('%B %d, %Y'),
                        'pages_left': pages_left,
                        'total_pages': total_pages,
                        'current_page': current_page,
                    }
            except Exception as e:
                logger.warning(f"Could not calculate reading stats: {e}")
    
    google_book_id = (book.get('googleBooksId') if book else None) or (book.get('id') if book else None)
    
    context = {
        'title': f"{book.get('title', 'Book Details')} - Book Details" if book else 'Book Details',
        'book': book,
        'in_catalog': in_catalog,
        'google_book_id': google_book_id,
        'reading_progress': reading_progress,
        'reading_stats': reading_stats,
        'user_clubs': user_clubs,
        'related_books': related_books,
    }
    return render(request, 'books/detail.html', context)


@jwt_login_required
@require_http_methods(["POST"])
def update_progress(request, book_id):
    """Update reading progress for a book."""
    try:
        current_page = request.POST.get('current_page')
        status = request.POST.get('status')
        
        # Validate inputs
        if current_page is None or status is None:
            messages.error(request, 'Current page and status are required')
            return redirect('books:detail', book_id=book_id)
        
        try:
            current_page = int(current_page)
        except ValueError:
            messages.error(request, 'Current page must be a number')
            return redirect('books:detail', book_id=book_id)
        
        # Prepare update data
        update_data = {
            'currentPage': current_page,
            'status': status
        }
        
        # Call FastAPI to update progress
        response = requests.put(
            f"{settings.FASTAPI_BACKEND_URL}/api/progress/{book_id}",
            json=update_data,
            headers=get_auth_headers(request),
            timeout=10
        )
        
        if response.status_code == 200:
            messages.success(request, 'Reading progress updated!')
        elif response.status_code == 404:
            messages.error(request, 'Reading progress not found. Please add the book to your catalog first.')
        else:
            messages.error(request, 'Unable to update reading progress')
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating progress for {book_id}: {e}")
        messages.error(request, 'Unable to connect to book service')
    
    return redirect('books:detail', book_id=book_id)


@jwt_login_required
@require_http_methods(["POST"])
def remove_book(request, book_id):
    """Remove book from user's catalog (delete reading progress)."""
    try:
        # Call FastAPI to delete reading progress
        response = requests.delete(
            f"{settings.FASTAPI_BACKEND_URL}/api/progress/{book_id}",
            headers=get_auth_headers(request),
            timeout=10
        )
        
        if response.status_code == 204:
            messages.success(request, 'Book removed from your catalog')
            return redirect('books:catalog')
        elif response.status_code == 404:
            messages.error(request, 'Book not found in your catalog')
        else:
            messages.error(request, 'Unable to remove book from catalog')
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error removing book {book_id}: {e}")
        messages.error(request, 'Unable to connect to book service')
    
    return redirect('books:detail', book_id=book_id)


# Keep old views for backward compatibility (redirects)
@jwt_login_required
def book_list(request):
    """Legacy redirect to catalog."""
    return redirect('books:catalog')