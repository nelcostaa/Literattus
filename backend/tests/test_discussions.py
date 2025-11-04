"""
Tests for Discussion API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.club import Club
from app.models.club_member import ClubMember
from app.models.book import Book
from app.models.discussion import Discussion


@pytest.fixture
def test_club(db_session: Session, test_user: User) -> Club:
    """Create a test club."""
    club = Club(
        name="Test Book Club",
        description="A test club",
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


def test_get_club_discussions_empty(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    auth_headers: dict
):
    """Test getting discussions for a club with no discussions."""
    response = client.get(
        f"/api/clubs/{test_club.id}/discussions",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json() == []


def test_create_discussion_success(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    test_book: Book,
    test_user: User,
    auth_headers: dict
):
    """Test creating a new discussion."""
    discussion_data = {
        "clubId": test_club.id,
        "bookId": test_book.id,
        "title": "What did you think of Chapter 1?",
        "content": "I found the opening quite intriguing!"
    }
    
    response = client.post(
        f"/api/clubs/{test_club.id}/discussions",
        json=discussion_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == discussion_data["title"]
    assert data["content"] == discussion_data["content"]
    assert data["clubId"] == test_club.id
    assert data["bookId"] == test_book.id
    assert data["userId"] == test_user.id
    assert data["parentId"] is None


def test_create_discussion_not_member(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    test_book: Book
):
    """Test that non-members cannot create discussions."""
    from app.core.security import get_REDACTED_hash
    
    # Create a different user who is not a member
    other_user = User(
        email="other@example.com",
        username="otheruser",
        REDACTED=get_REDACTED_hash("otherREDACTED"),
        firstName="Other",
        lastName="User"
    )
    db_session.add(other_user)
    db_session.commit()
    
    # Login as other user to get token
    login_response = client.post("/api/auth/login", json={
        "email": "other@example.com",
        "REDACTED": "otherREDACTED"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    discussion_data = {
        "clubId": test_club.id,
        "bookId": test_book.id,
        "title": "Test Discussion",
        "content": "Test content"
    }
    
    response = client.post(
        f"/api/clubs/{test_club.id}/discussions",
        json=discussion_data,
        headers=headers
    )
    
    assert response.status_code == 403
    assert "must be a member" in response.json()["detail"]


def test_create_discussion_invalid_book(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    auth_headers: dict
):
    """Test creating discussion with non-existent book."""
    discussion_data = {
        "clubId": test_club.id,
        "bookId": "notfound123",  # Valid format but doesn't exist
        "title": "Test Discussion",
        "content": "Test content"
    }
    
    response = client.post(
        f"/api/clubs/{test_club.id}/discussions",
        json=discussion_data,
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert "Book not found" in response.json()["detail"]


def test_get_discussion_by_id(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    test_book: Book,
    test_user: User,
    auth_headers: dict
):
    """Test getting a specific discussion by ID."""
    # Create a discussion first
    discussion = Discussion(
        clubId=test_club.id,
        userId=test_user.id,
        bookId=test_book.id,
        title="Test Discussion",
        content="Test content"
    )
    db_session.add(discussion)
    db_session.commit()
    db_session.refresh(discussion)
    
    response = client.get(
        f"/api/clubs/discussions/{discussion.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == discussion.id
    assert data["title"] == discussion.title
    assert data["content"] == discussion.content


def test_update_discussion_success(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    test_book: Book,
    test_user: User,
    auth_headers: dict
):
    """Test updating a discussion by its author."""
    # Create a discussion
    discussion = Discussion(
        clubId=test_club.id,
        userId=test_user.id,
        bookId=test_book.id,
        title="Original Title",
        content="Original content"
    )
    db_session.add(discussion)
    db_session.commit()
    db_session.refresh(discussion)
    
    # Update it
    update_data = {
        "title": "Updated Title",
        "content": "Updated content"
    }
    
    response = client.put(
        f"/api/clubs/discussions/{discussion.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content"


def test_delete_discussion_success(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    test_book: Book,
    test_user: User,
    auth_headers: dict
):
    """Test deleting a discussion by its author."""
    # Create a discussion
    discussion = Discussion(
        clubId=test_club.id,
        userId=test_user.id,
        bookId=test_book.id,
        title="Test Discussion",
        content="Test content"
    )
    db_session.add(discussion)
    db_session.commit()
    discussion_id = discussion.id
    
    # Delete it
    response = client.delete(
        f"/api/clubs/discussions/{discussion_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify it's deleted
    deleted = db_session.query(Discussion).filter(Discussion.id == discussion_id).first()
    assert deleted is None


def test_get_discussion_replies(
    client: TestClient,
    db_session: Session,
    test_club: Club,
    test_book: Book,
    test_user: User,
    auth_headers: dict
):
    """Test getting replies to a discussion."""
    # Create parent discussion
    parent = Discussion(
        clubId=test_club.id,
        userId=test_user.id,
        bookId=test_book.id,
        title="Parent Discussion",
        content="Parent content"
    )
    db_session.add(parent)
    db_session.commit()
    db_session.refresh(parent)
    
    # Create replies
    reply1 = Discussion(
        clubId=test_club.id,
        userId=test_user.id,
        bookId=test_book.id,
        parentId=parent.id,
        content="Reply 1"
    )
    reply2 = Discussion(
        clubId=test_club.id,
        userId=test_user.id,
        bookId=test_book.id,
        parentId=parent.id,
        content="Reply 2"
    )
    db_session.add_all([reply1, reply2])
    db_session.commit()
    
    # Get replies
    response = client.get(
        f"/api/clubs/discussions/{parent.id}/replies",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(r["parentId"] == parent.id for r in data)

