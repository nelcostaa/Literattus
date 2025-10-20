"""
Tests for books endpoints.
"""

import pytest


def test_create_book(client, auth_headers):
    """Test creating a book."""
    response = client.post("/api/books/", headers=auth_headers, json={
        "googleBooksId": "test123",
        "title": "Test Book",
        "author": "Test Author",
        "pageCount": 300,
        "averageRating": 4.5
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"
    assert data["author"] == "Test Author"


def test_get_books(client, auth_headers):
    """Test getting list of books."""
    # Create a book first
    client.post("/api/books/", headers=auth_headers, json={
        "googleBooksId": "test456",
        "title": "Another Book",
        "author": "Another Author"
    })
    
    response = client.get("/api/books/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_book_by_id(client, auth_headers):
    """Test getting a specific book."""
    # Create a book
    create_response = client.post("/api/books/", headers=auth_headers, json={
        "googleBooksId": "test789",
        "title": "Specific Book",
        "author": "Specific Author"
    })
    
    book_id = create_response.json()["id"]
    
    response = client.get(f"/api/books/{book_id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == "Specific Book"


def test_update_book(client, auth_headers):
    """Test updating a book."""
    # Create a book
    create_response = client.post("/api/books/", headers=auth_headers, json={
        "googleBooksId": "update123",
        "title": "Original Title",
        "author": "Original Author"
    })
    
    book_id = create_response.json()["id"]
    
    # Update the book
    response = client.put(f"/api/books/{book_id}", headers=auth_headers, json={
        "title": "Updated Title"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["author"] == "Original Author"  # Unchanged


def test_delete_book(client, auth_headers):
    """Test deleting a book."""
    # Create a book
    create_response = client.post("/api/books/", headers=auth_headers, json={
        "googleBooksId": "delete123",
        "title": "To Delete",
        "author": "Delete Author"
    })
    
    book_id = create_response.json()["id"]
    
    # Delete the book
    response = client.delete(f"/api/books/{book_id}", headers=auth_headers)
    
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/books/{book_id}", headers=auth_headers)
    assert get_response.status_code == 404

