"""
Books API endpoints.
Handles book catalog management and Google Books integration.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate, BookResponse, BookSearch
from app.services.google_books import google_books_service

router = APIRouter()


@router.get("/", response_model=List[BookResponse])
async def get_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of books from local catalog (paginated).
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[BookResponse]: List of books
    """
    books = db.query(Book).offset(skip).limit(limit).all()
    return books


@router.get("/search")
async def search_books(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    max_results: int = Query(10, ge=1, le=40, description="Maximum results"),
    start_index: int = Query(0, ge=0, description="Start index for pagination"),
    current_user: User = Depends(get_current_user)
):
    """
    Search books using Google Books API.
    
    Args:
        q: Search query string
        max_results: Maximum number of results
        start_index: Starting index for pagination
        current_user: Current authenticated user
        
    Returns:
        dict: Search results from Google Books
    """
    results = await google_books_service.search_books(
        query=q,
        max_results=max_results,
        start_index=start_index
    )
    
    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get book by ID from local catalog.
    
    Args:
        book_id: Book ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        BookResponse: Book object
        
    Raises:
        HTTPException: If book not found
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    return book


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a new book to the catalog.
    
    Args:
        book_data: Book creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        BookResponse: Created book object
        
    Raises:
        HTTPException: If book with Google Books ID already exists
    """
    # Check if book already exists
    existing_book = db.query(Book).filter(
        Book.googleBooksId == book_data.googleBooksId
    ).first()
    
    if existing_book:
        return existing_book  # Return existing book instead of error
    
    # Create new book
    genres_str = ",".join(book_data.genres) if book_data.genres else None
    
    new_book = Book(
        googleBooksId=book_data.googleBooksId,
        title=book_data.title,
        author=book_data.author,
        isbn=book_data.isbn,
        description=book_data.description,
        coverImage=book_data.coverImage,
        publishedDate=book_data.publishedDate,
        pageCount=book_data.pageCount,
        genres=genres_str,
        averageRating=book_data.averageRating
    )
    
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    return new_book


@router.get("/google/{google_books_id}")
async def get_book_from_google(
    google_books_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get book details from Google Books API.
    
    Args:
        google_books_id: Google Books volume ID
        current_user: Current authenticated user
        
    Returns:
        dict: Book data from Google Books
        
    Raises:
        HTTPException: If book not found on Google Books
    """
    book_data = await google_books_service.get_book_by_id(google_books_id)
    
    if not book_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found on Google Books"
        )
    
    return book_data


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update book information.
    
    Args:
        book_id: Book ID
        book_data: Updated book data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        BookResponse: Updated book object
        
    Raises:
        HTTPException: If book not found
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Update fields if provided
    if book_data.title is not None:
        book.title = book_data.title
    if book_data.author is not None:
        book.author = book_data.author
    if book_data.isbn is not None:
        book.isbn = book_data.isbn
    if book_data.description is not None:
        book.description = book_data.description
    if book_data.coverImage is not None:
        book.coverImage = book_data.coverImage
    if book_data.publishedDate is not None:
        book.publishedDate = book_data.publishedDate
    if book_data.pageCount is not None:
        book.pageCount = book_data.pageCount
    if book_data.genres is not None:
        book.genres = ",".join(book_data.genres)
    if book_data.averageRating is not None:
        book.averageRating = book_data.averageRating
    
    db.commit()
    db.refresh(book)
    
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a book from the catalog.
    
    Args:
        book_id: Book ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        None
        
    Raises:
        HTTPException: If book not found
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    db.delete(book)
    db.commit()
    
    return None

