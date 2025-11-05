"""
Clubs views - handles book club pages and management.
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
def club_list(request):
    """
    Display list of book clubs with real data from FastAPI backend.
    Fetches clubs and determines user membership status.
    """
    clubs = []
    user_club_ids = set()
    headers = get_auth_headers(request)
    
    try:
        # 1. Fetch all clubs (public clubs + user's private clubs)
        clubs_response = requests.get(
            f"{settings.FASTAPI_BACKEND_URL}/api/clubs/",
            headers=headers,
            timeout=10
        )
        
        if clubs_response.status_code == 200:
            clubs = clubs_response.json()
        else:
            logger.warning(f"Failed to fetch clubs: {clubs_response.status_code}")
            messages.warning(request, 'Unable to load clubs')
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching clubs: {e}")
        messages.error(request, 'Unable to connect to club service')
    
    try:
        # 2. Fetch user's clubs to determine membership
        my_clubs_response = requests.get(
            f"{settings.FASTAPI_BACKEND_URL}/api/clubs/my-clubs",
            headers=headers,
            timeout=10
        )
        
        if my_clubs_response.status_code == 200:
            my_clubs = my_clubs_response.json()
            user_club_ids = {club.get('id') for club in my_clubs}
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"Could not fetch user's clubs: {e}")
    
    # 3. Enrich clubs with additional data (member count, current book, discussion count)
    # Note: This makes multiple API calls per club. For better performance, consider
    # adding these fields to the club response endpoint in the future.
    enriched_clubs = []
    for club in clubs:
        club_id = club.get('id')
        is_member = club_id in user_club_ids
        
        # Fetch members for member count (only if we have a few clubs)
        member_count = 0
        current_book = None
        discussion_count = 0
        
        # Only fetch extra data for first 20 clubs to avoid performance issues
        if len(enriched_clubs) < 20:
            try:
                members_response = requests.get(
                    f"{settings.FASTAPI_BACKEND_URL}/api/clubs/{club_id}/members",
                    headers=headers,
                    timeout=5
                )
                if members_response.status_code == 200:
                    members = members_response.json()
                    member_count = len(members)
            except requests.exceptions.RequestException:
                pass
            
            # Fetch current book
            try:
                current_book_response = requests.get(
                    f"{settings.FASTAPI_BACKEND_URL}/api/clubs/{club_id}/books/current",
                    headers=headers,
                    timeout=5
                )
                if current_book_response.status_code == 200:
                    current_book_data = current_book_response.json()
                    # Fetch book details
                    book_response = requests.get(
                        f"{settings.FASTAPI_BACKEND_URL}/api/books/{current_book_data.get('bookId')}",
                        headers=headers,
                        timeout=5
                    )
                    if book_response.status_code == 200:
                        current_book = book_response.json()
            except requests.exceptions.RequestException:
                pass
            
            # Fetch discussion count (limit to 10 to get a sense of activity)
            try:
                discussions_response = requests.get(
                    f"{settings.FASTAPI_BACKEND_URL}/api/clubs/{club_id}/discussions",
                    headers=headers,
                    params={'limit': 10},
                    timeout=5
                )
                if discussions_response.status_code == 200:
                    discussions = discussions_response.json()
                    discussion_count = len(discussions)
            except requests.exceptions.RequestException:
                pass
        
        # Add enriched data
        enriched_club = {
            **club,
            'member_count': member_count,
            'current_book': current_book,
            'discussion_count': discussion_count,
            'is_member': is_member,
        }
        enriched_clubs.append(enriched_club)
    
    context = {
        'title': 'Book Clubs',
        'clubs': enriched_clubs,
    }
    return render(request, 'clubs/club_list.html', context)


@jwt_login_required
def club_detail(request, club_id):
    """
    Display comprehensive club details including members, current book, discussions, and upcoming books.
    Determines user's role in the club for permission-based actions.
    """
    club = None
    members = []
    discussions = []
    club_books = []
    current_book = None
    upcoming_books = []
    user_role = None
    is_member = False
    is_owner = False
    
    headers = get_auth_headers(request)
    user_id = request.session.get('user_id')
    
    try:
        # 1. Fetch club basic details
        response = requests.get(
            f"{settings.FASTAPI_BACKEND_URL}/api/clubs/{club_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            club = response.json()
        elif response.status_code == 404:
            messages.error(request, 'Club not found')
            return redirect('clubs:list')
        elif response.status_code == 403:
            messages.error(request, "You don't have access to this private club")
            return redirect('clubs:list')
        else:
            messages.warning(request, 'Unable to load club details')
            return redirect('clubs:list')
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching club {club_id}: {e}")
        messages.error(request, 'Unable to connect to club service')
        return redirect('clubs:list')
    
    if not club:
        return redirect('clubs:list')
    
    try:
        # 2. Fetch club members
        members_response = requests.get(
            f"{settings.FASTAPI_BACKEND_URL}/api/clubs/{club_id}/members",
            headers=headers,
            timeout=10
        )
        
        if members_response.status_code == 200:
            members = members_response.json()
            
            # Determine user's role
            for member in members:
                if member.get('userId') == user_id:
                    is_member = True
                    user_role = member.get('role')
                    is_owner = (user_role == 'owner')
                    break
                    
    except requests.exceptions.RequestException as e:
        logger.warning(f"Could not fetch club members: {e}")
    
    try:
        # 3. Fetch club books (all statuses)
        books_response = requests.get(
            f"{settings.FASTAPI_BACKEND_URL}/api/clubs/{club_id}/books",
            headers=headers,
            timeout=10
        )
        
        if books_response.status_code == 200:
            club_books = books_response.json()
            
            # Separate current book from upcoming/voted books
            for book_entry in club_books:
                if book_entry.get('status') == 'current':
                    current_book = book_entry
                elif book_entry.get('status') in ['planned', 'voted']:
                    upcoming_books.append(book_entry)
                    
    except requests.exceptions.RequestException as e:
        logger.warning(f"Could not fetch club books: {e}")
    
    # Fetch full book details for current book if exists
    if current_book and current_book.get('bookId'):
        try:
            book_response = requests.get(
                f"{settings.FASTAPI_BACKEND_URL}/api/books/{current_book.get('bookId')}",
                headers=headers,
                timeout=10
            )
            
            if book_response.status_code == 200:
                book_data = book_response.json()
                # Merge book details into current_book dict
                current_book['book'] = book_data
            else:
                logger.warning(f"Could not fetch book details for {current_book.get('bookId')}")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error fetching book details: {e}")
    
    try:
        # 4. Fetch club discussions (top-level only)
        discussions_response = requests.get(
            f"{settings.FASTAPI_BACKEND_URL}/api/clubs/{club_id}/discussions",
            headers=headers,
            params={'limit': 10},
            timeout=10
        )
        
        if discussions_response.status_code == 200:
            discussions = discussions_response.json()
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"Could not fetch club discussions: {e}")
    
    # Calculate member count
    member_count = len(members)
    
    # Count discussions
    discussion_count = len(discussions)
    
    # Count completed books
    completed_count = sum(1 for book in club_books if book.get('status') == 'completed')
    
    context = {
        'title': f"{club.get('name', 'Club Details')} - Literattus",
        'club': club,
        'members': members,
        'member_count': member_count,
        'discussions': discussions,
        'discussion_count': discussion_count,
        'current_book': current_book,
        'upcoming_books': upcoming_books,
        'completed_count': completed_count,
        'is_member': is_member,
        'is_owner': is_owner,
        'user_role': user_role,
    }
    
    return render(request, 'clubs/club_detail.html', context)


@jwt_login_required
def my_clubs(request):
    """Display user's clubs."""
    # TODO: Fetch from FastAPI backend
    context = {
        'title': 'My Clubs',
    }
    return render(request, 'clubs/my_clubs.html', context)


@require_http_methods(["POST"])
@jwt_login_required
def join_club(request, club_id):
    """
    Join a book club.
    Calls FastAPI backend POST /api/clubs/{club_id}/join.
    """
    try:
        headers = get_auth_headers(request)
        response = requests.post(
            f"{settings.FASTAPI_BACKEND_URL}/api/clubs/{club_id}/join",
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            messages.success(request, 'Successfully joined the club!')
        elif response.status_code == 400:
            try:
                error_detail = response.json().get('detail', 'Unable to join club')
                messages.error(request, error_detail)
            except (ValueError, KeyError):
                messages.error(request, 'Unable to join club. Please try again.')
        elif response.status_code == 404:
            messages.error(request, 'Club not found')
        elif response.status_code == 403:
            messages.error(request, 'You do not have permission to join this club')
        else:
            logger.warning(f"Unexpected status code {response.status_code} when joining club {club_id}")
            messages.warning(request, 'Unable to join club at this time. Please try again.')
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error joining club {club_id}: {e}")
        messages.error(request, 'Unable to connect to club service. Please try again.')
    
    return redirect('clubs:detail', club_id=club_id)


@require_http_methods(["POST"])
@jwt_login_required
def leave_club(request, club_id):
    """
    Leave a book club.
    Calls FastAPI backend POST /api/clubs/{club_id}/leave.
    """
    try:
        headers = get_auth_headers(request)
        response = requests.post(
            f"{settings.FASTAPI_BACKEND_URL}/api/clubs/{club_id}/leave",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 204:
            messages.success(request, 'You have left the club')
            return redirect('clubs:list')
        elif response.status_code == 400:
            error_detail = response.json().get('detail', 'Unable to leave club')
            messages.error(request, error_detail)
        elif response.status_code == 404:
            messages.error(request, 'Club not found')
        else:
            messages.warning(request, 'Unable to leave club at this time')
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error leaving club {club_id}: {e}")
        messages.error(request, 'Unable to connect to club service')
    
    return redirect('clubs:detail', club_id=club_id)


@jwt_login_required
def edit_club(request, club_id):
    """
    Edit club settings (owner only).
    TODO: Implement club editing form and PUT request to backend.
    """
    messages.info(request, 'Club editing feature coming soon!')
    return redirect('clubs:detail', club_id=club_id)

