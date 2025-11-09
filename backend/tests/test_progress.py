"""
Tests for reading progress endpoints.
"""

import pytest
from datetime import datetime


def test_get_reading_progress_success(client, auth_headers, db_session, test_user, test_book):
    """Test getting reading progress for a book."""
    from app.models.reading_progress import ReadingProgress
    
    # Create reading progress using the same db_session
    progress = ReadingProgress(
        userId=test_user.id,
        bookId=test_book.id,
        status="reading",
        currentPage=100,
        progressPercentage=33.33
    )
    db_session.add(progress)
    db_session.commit()
    
    response = client.get(f"/api/progress/{test_book.id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "reading"
    assert data["currentPage"] == 100
    assert data["progressPercentage"] == 33.33
    assert data["bookId"] == test_book.id
    assert data["userId"] == test_user.id


def test_get_reading_progress_not_found(client, auth_headers, test_book):
    """Test getting reading progress for a book that doesn't have progress."""
    response = client.get(f"/api/progress/{test_book.id}", headers=auth_headers)
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_reading_progress_book_not_found(client, auth_headers):
    """Test getting reading progress for a non-existent book."""
    response = client.get("/api/progress/nonexistent", headers=auth_headers)
    
    assert response.status_code == 404
    assert "book not found" in response.json()["detail"].lower()


def test_update_reading_progress_success(client, auth_headers, db_session, test_user, test_book):
    """Test updating reading progress."""
    from app.models.reading_progress import ReadingProgress
    
    # Create initial reading progress using the same db_session
    progress = ReadingProgress(
        userId=test_user.id,
        bookId=test_book.id,
        status="not_started",
        currentPage=0,
        progressPercentage=0.0
    )
    db_session.add(progress)
    db_session.commit()
    
    # Update progress
    update_data = {
        "currentPage": 150,
        "status": "reading"
    }
    response = client.put(
        f"/api/progress/{test_book.id}",
        headers=auth_headers,
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["currentPage"] == 150
    assert data["status"] == "reading"
    # Progress percentage should be recalculated (150/300 = 50%)
    assert data["progressPercentage"] == 50.0


def test_update_reading_progress_to_completed(client, auth_headers, db_session, test_user, test_book):
    """Test updating reading progress to completed status."""
    from app.models.reading_progress import ReadingProgress
    
    # Create initial reading progress using the same db_session
    progress = ReadingProgress(
        userId=test_user.id,
        bookId=test_book.id,
        status="reading",
        currentPage=200,
        progressPercentage=66.67
    )
    db_session.add(progress)
    db_session.commit()
    
    # Update to completed
    update_data = {
        "status": "completed"
    }
    response = client.put(
        f"/api/progress/{test_book.id}",
        headers=auth_headers,
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["progressPercentage"] == 100.0
    assert data["completedAt"] is not None


def test_delete_reading_progress_success(client, auth_headers, db_session, test_user, test_book):
    """Test deleting reading progress."""
    from app.models.reading_progress import ReadingProgress
    
    # Create reading progress using the same db_session
    progress = ReadingProgress(
        userId=test_user.id,
        bookId=test_book.id,
        status="reading",
        currentPage=100,
        progressPercentage=33.33
    )
    db_session.add(progress)
    db_session.commit()
    
    # Delete progress
    response = client.delete(f"/api/progress/{test_book.id}", headers=auth_headers)
    
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/progress/{test_book.id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_delete_reading_progress_not_found(client, auth_headers, test_book):
    """Test deleting reading progress that doesn't exist."""
    response = client.delete(f"/api/progress/{test_book.id}", headers=auth_headers)
    
    assert response.status_code == 404

