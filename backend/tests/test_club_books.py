"""
Tests for Club Books API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.club import Club
from app.models.club_member import ClubMember
from app.models.book import Book
from app.models.club_book import ClubBook


@pytest.fixture
def test_club(db_session: Session, test_user: User) -> Club:
    """Create a test club."""
    club = Club(
        name="Book Test Club",
        description="A club for book testing",
        createdById=test_user.id
    )
    db_session.add(club)
    db_session.commit()
    db_session.refresh(club)
    
    # Add creator as owner member
    membership = ClubMember(
        userId=test_user.id,
        clubId=club.id,
        role="owner"
    )
    db_session.add(membership)
    db_session.commit()
    
    return club


def test_get_club_books_empty(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    auth_headers: dict
):
    """Test getting books for a club with no books."""
    response = client.get(
        f"/api/clubs/{test_club.id}/books",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json() == []


def test_nominate_book_success(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    test_book: Book,
    auth_headers: dict
):
    """Test nominating a book for the club."""
    book_data = {
        "clubId": test_club.id,
        "bookId": test_book.id,
        "status": "voted"
    }
    
    response = client.post(
        f"/api/clubs/{test_club.id}/books/nominate",
        json=book_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["clubId"] == test_club.id
    assert data["bookId"] == test_book.id
    assert data["status"] == "voted"


def test_nominate_book_not_member(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    test_book: Book
):
    """Test that non-members cannot nominate books."""
    from app.core.security import get_REDACTED_hash
    
    # Create a different user who is not a member
    other_user = User(
        email="other_book@example.com",
        username="otherbookuser",
        REDACTED=get_REDACTED_hash("otherbookREDACTED"),
        firstName="Other",
        lastName="BookUser"
    )
    db_session.add(other_user)
    db_session.commit()
    
    # Login as other user
    login_response = client.post("/api/auth/login", json={
        "email": "other_book@example.com",
        "REDACTED": "otherbookREDACTED"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    book_data = {
        "clubId": test_club.id,
        "bookId": test_book.id,
        "status": "voted"
    }
    
    response = client.post(
        f"/api/clubs/{test_club.id}/books/nominate",
        json=book_data,
        headers=headers
    )
    
    assert response.status_code == 403
    assert "must be a member" in response.json()["detail"]


def test_nominate_book_already_nominated(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    test_book: Book,
    auth_headers: dict
):
    """Test nominating a book that's already in the club."""
    # Add book to club first
    club_book = ClubBook(
        clubId=test_club.id,
        bookId=test_book.id,
        status="voted"
    )
    db_session.add(club_book)
    db_session.commit()
    
    # Try to nominate again
    book_data = {
        "clubId": test_club.id,
        "bookId": test_book.id,
        "status": "voted"
    }
    
    response = client.post(
        f"/api/clubs/{test_club.id}/books/nominate",
        json=book_data,
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "already nominated" in response.json()["detail"]


def test_update_club_book_status(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    test_book: Book,
    auth_headers: dict
):
    """Test updating a club book status (owner/admin only)."""
    # Add book to club first
    club_book = ClubBook(
        clubId=test_club.id,
        bookId=test_book.id,
        status="voted"
    )
    db_session.add(club_book)
    db_session.commit()
    
    # Update to current
    update_data = {
        "status": "current"
    }
    
    response = client.put(
        f"/api/clubs/{test_club.id}/books/{test_book.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "current"
    assert data["startedAt"] is not None


def test_update_club_book_to_completed(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    test_book: Book,
    auth_headers: dict
):
    """Test marking a club book as completed."""
    # Add book to club as current
    club_book = ClubBook(
        clubId=test_club.id,
        bookId=test_book.id,
        status="current"
    )
    db_session.add(club_book)
    db_session.commit()
    
    # Update to completed
    update_data = {
        "status": "completed"
    }
    
    response = client.put(
        f"/api/clubs/{test_club.id}/books/{test_book.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["completedAt"] is not None


def test_get_current_club_book(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    test_book: Book,
    auth_headers: dict
):
    """Test getting the club's current book."""
    # Add book to club as current
    club_book = ClubBook(
        clubId=test_club.id,
        bookId=test_book.id,
        status="current"
    )
    db_session.add(club_book)
    db_session.commit()
    
    response = client.get(
        f"/api/clubs/{test_club.id}/books/current",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["bookId"] == test_book.id
    assert data["status"] == "current"


def test_get_current_club_book_none(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    auth_headers: dict
):
    """Test getting current book when club has none."""
    response = client.get(
        f"/api/clubs/{test_club.id}/books/current",
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert "no current book" in response.json()["detail"]


def test_remove_club_book(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    test_book: Book,
    auth_headers: dict
):
    """Test removing a book from club (admin only)."""
    # Add book to club first
    club_book = ClubBook(
        clubId=test_club.id,
        bookId=test_book.id,
        status="voted"
    )
    db_session.add(club_book)
    db_session.commit()
    
    # Remove it
    response = client.delete(
        f"/api/clubs/{test_club.id}/books/{test_book.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify it's deleted
    deleted = db_session.query(ClubBook).filter(
        ClubBook.clubId == test_club.id,
        ClubBook.bookId == test_book.id
    ).first()
    assert deleted is None


def test_get_club_books_filtered(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    auth_headers: dict
):
    """Test getting club books filtered by status."""
    # Create books with different statuses
    book1 = Book(id="book1", title="Book 1", author="Author 1")
    book2 = Book(id="book2", title="Book 2", author="Author 2")
    book3 = Book(id="book3", title="Book 3", author="Author 3")
    db_session.add_all([book1, book2, book3])
    db_session.commit()
    
    # Add to club with different statuses
    club_book1 = ClubBook(clubId=test_club.id, bookId="book1", status="current")
    club_book2 = ClubBook(clubId=test_club.id, bookId="book2", status="voted")
    club_book3 = ClubBook(clubId=test_club.id, bookId="book3", status="completed")
    db_session.add_all([club_book1, club_book2, club_book3])
    db_session.commit()
    
    # Get only voted books
    response = client.get(
        f"/api/clubs/{test_club.id}/books?status_filter=voted",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["bookId"] == "book2"
    assert data[0]["status"] == "voted"

