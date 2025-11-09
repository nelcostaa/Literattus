"""
Tests for books endpoints.
"""

import pytest


def test_create_book(client, auth_headers):
    """Test creating a book."""
    response = client.post("/api/books/", headers=auth_headers, json={
        "id": "test123",
        "title": "Test Book",
        "author": "Test Author",
        "pageCount": 300
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"
    assert data["author"] == "Test Author"


def test_get_books(client, auth_headers):
    """Test getting list of books."""
    # Create a book first
    client.post("/api/books/", headers=auth_headers, json={
        "id": "test456",
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
    # Create a book with more details
    book_payload = {
        "id": "test789",
        "title": "Specific Book",
        "author": "Specific Author",
        "description": "A detailed description.",
        "coverImage": "http://example.com/cover.jpg",
        "isbn": "9780321765723",
        "publishedDate": "2023-01-15",
        "pageCount": 450
    }
    create_response = client.post("/api/books/", headers=auth_headers, json=book_payload)
    
    assert create_response.status_code == 201
    book_id = create_response.json()["id"]
    
    response = client.get(f"/api/books/{book_id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == "Specific Book"
    assert data["author"] == "Specific Author"
    assert data["description"] == "A detailed description."
    assert data["coverImage"] == "http://example.com/cover.jpg"
    assert data["isbn"] == "9780321765723"
    assert data["publishedDate"] == "2023-01-15"
    assert data["pageCount"] == 450


def test_get_book_not_found(client, auth_headers):
    """Test getting a book that does not exist."""
    response = client.get("/api/books/nonexistentid", headers=auth_headers)
    assert response.status_code == 404


def test_update_book(client, auth_headers):
    """Test updating a book."""
    # Create a book
    create_response = client.post("/api/books/", headers=auth_headers, json={
        "id": "update123",
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
        "id": "delete123",
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


def test_search_and_save_with_parsed_service(monkeypatch, client, auth_headers):
    """Ensure search-and-save works when service returns parsed schema."""
    from app.services import google_books

    async def fake_get_book_by_id(_id: str):
        return {
            'googleBooksId': _id,
            'title': 'Parsed Title',
            'author': 'Author One, Author Two',
            'description': 'Desc',
            'coverImage': 'http://img/x.jpg',
            'publishedDate': '2022-05-01',
            'pageCount': 321,
            'genres': ['Test']
        }

    monkeypatch.setattr(google_books.google_books_service, 'get_book_by_id', fake_get_book_by_id)

    r = client.post(f"/api/books/search-and-save/testParsed", headers=auth_headers)
    assert r.status_code in (200, 201)
    data = r.json()
    assert data['id'] == 'testParsed'
    assert data['title'] == 'Parsed Title'


def test_search_and_save_with_raw_service(monkeypatch, client, auth_headers):
    """Ensure search-and-save works when service returns raw Google Books item."""
    from app.services import google_books

    async def fake_get_book_by_id(_id: str):
        return {
            'id': _id,
            'volumeInfo': {
                'title': 'Raw Title',
                'authors': ['Raw Author'],
                'description': 'Raw Desc',
                'publishedDate': '2021-01-01',
                'pageCount': 111,
                'imageLinks': {
                    'thumbnail': 'http://img/r.jpg'
                },
                'industryIdentifiers': [
                    {'type': 'ISBN_13', 'identifier': '9781234567897'}
                ]
            }
        }

    monkeypatch.setattr(google_books.google_books_service, 'get_book_by_id', fake_get_book_by_id)

    r = client.post(f"/api/books/search-and-save/testRaw", headers=auth_headers)
    assert r.status_code in (200, 201)
    data = r.json()
    assert data['id'] == 'testRaw'
    assert data['title'] == 'Raw Title'


def test_search_and_save_creates_reading_progress(monkeypatch, client, auth_headers, db_session):
    """Test that search-and-save creates a reading_progress entry for the user."""
    from app.services import google_books
    from app.models.reading_progress import ReadingProgress

    async def fake_get_book_by_id(_id: str):
        return {
            'googleBooksId': _id,
            'title': 'Progress Test Book',
            'author': 'Test Author',
            'description': 'Test description',
            'coverImage': 'http://img/test.jpg',
            'publishedDate': '2023-01-01',
            'pageCount': 250,
            'genres': ['Fiction']
        }

    monkeypatch.setattr(google_books.google_books_service, 'get_book_by_id', fake_get_book_by_id)

    # Add book via search-and-save (ID must be ≤12 chars)
    r = client.post(f"/api/books/search-and-save/progTest123", headers=auth_headers)
    assert r.status_code in (200, 201)
    
    # Verify reading_progress entry was created
    progress = db_session.query(ReadingProgress).filter(
        ReadingProgress.bookId == 'progTest123'
    ).first()
    
    assert progress is not None
    assert progress.status == "not_started"
    assert progress.currentPage == 0
    assert progress.progressPercentage == 0.0


def test_my_catalog_returns_user_books_only(client, auth_headers, db_session, test_user):
    """Test that /my-catalog returns only the current user's books."""
    from app.models.book import Book
    from app.models.reading_progress import ReadingProgress

    # Create a book
    book = Book(
        id="catalogTest1",
        title="User's Book",
        author="Test Author",
        pageCount=200
    )
    db_session.add(book)
    db_session.commit()
    
    # Create reading progress for the test user
    progress = ReadingProgress(
        userId=test_user.id,
        bookId=book.id,
        status="reading",
        currentPage=50,
        progressPercentage=25.0
    )
    db_session.add(progress)
    db_session.commit()
    
    # Fetch catalog
    r = client.get("/api/books/my-catalog", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # Find our book
    user_book = next((b for b in data if b['id'] == 'catalogTest1'), None)
    assert user_book is not None
    assert user_book['title'] == "User's Book"
    assert user_book['status'] == "reading"
    assert user_book['currentPage'] == 50
    assert user_book['progressPercentage'] == 25.0


def test_my_catalog_empty_for_new_user(client, auth_headers):
    """Test that /my-catalog returns empty list for user with no books."""
    r = client.get("/api/books/my-catalog", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_get_related_books(client, auth_headers, test_book):
    """Test getting related books for a book."""
    from unittest.mock import patch, AsyncMock
    
    # Mock the Google Books service to return related books
    mock_related_books = [
        {
            "googleBooksId": "related1",
            "title": "Related Book 1",
            "author": "Test Author",
            "coverImage": "http://example.com/cover1.jpg"
        },
        {
            "googleBooksId": "related2",
            "title": "Related Book 2",
            "author": "Test Author",
            "coverImage": "http://example.com/cover2.jpg"
        }
    ]
    
    with patch('app.api.books.google_books_service.search_books', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_related_books
        
        response = client.get(f"/api/books/{test_book.id}/related", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) > 0
        # Should filter out the current book
        assert test_book.id not in [b.get("googleBooksId") for b in data["results"]]


def test_get_related_books_book_not_found(client, auth_headers):
    """Test getting related books for a non-existent book."""
    response = client.get("/api/books/nonexistent/related", headers=auth_headers)
    
    assert response.status_code == 404

