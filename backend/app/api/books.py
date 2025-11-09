"""
Books API endpoints.
Handles book catalog management and Google Books integration.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from loguru import logger

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
    DEPRECATED: Use /my-catalog for user-specific books with reading progress.
    
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


@router.get("/my-catalog")
async def get_my_catalog(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's personal catalog with reading progress data.
    Returns books the user has added, joined with their reading_progress.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[dict]: Books with reading progress data
    """
    from app.models.reading_progress import ReadingProgress
    
    # Query reading_progress for this user, joined with book data
    progress_entries = db.query(
        ReadingProgress,
        Book
    ).join(
        Book, ReadingProgress.bookId == Book.id
    ).filter(
        ReadingProgress.userId == current_user.id
    ).offset(skip).limit(limit).all()
    
    # Transform to dict with both progress and book info
    result = []
    for progress, book in progress_entries:
        result.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'description': book.description,
            'coverImage': book.coverImage,
            'isbn': book.isbn,
            'publishedDate': book.publishedDate.isoformat() if book.publishedDate else None,
            'pageCount': book.pageCount,
            'createdAt': book.createdAt.isoformat() if book.createdAt else None,
            'updatedAt': book.updatedAt.isoformat() if book.updatedAt else None,
            # Reading progress fields
            'status': progress.status,
            'currentPage': progress.currentPage,
            'progressPercentage': progress.progressPercentage,
            'rating': progress.rating,
            'review': progress.review,
            'startedAt': progress.startedAt.isoformat() if progress.startedAt else None,
            'completedAt': progress.completedAt.isoformat() if progress.completedAt else None,
        })
    
    logger.info(f"Fetched {len(result)} books from user {current_user.id}'s catalog")
    return result


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
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get book by Google Books ID from local catalog.
    
    Args:
        book_id: Google Books ID (string, max 12 chars)
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
    existing_book = db.query(Book).filter(Book.id == book_data.id).first()
    
    if existing_book:
        return existing_book  # Return existing book instead of error
    
    # Create new book using BookCreate schema
    new_book = Book(**book_data.model_dump())
    
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    logger.info(f"Created new book: {new_book.title} (ID: {new_book.id})")
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
    book_id: str,
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
    
    db.commit()
    db.refresh(book)
    
    return book


@router.post("/search-and-save/{google_book_id}", response_model=BookResponse)
async def search_and_save_book(
    google_book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch book from Google Books API and save to database.
    Also creates a reading_progress entry for the current user.
    
    Workflow:
    1. Check if book already exists in DB
    2. If not, fetch from Google Books API
    3. Transform and save to database
    4. Create reading_progress entry for user (status: not_started)
    5. Return saved book
    
    Args:
        google_book_id: Google Books volume ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        BookResponse: Saved book object
        
    Raises:
        HTTPException: If book not found in Google Books
    """
    from app.services.google_books import transform_to_book_create
    from app.models.reading_progress import ReadingProgress
    
    # Check if book exists in database
    existing_book = db.query(Book).filter(Book.id == google_book_id).first()
    book_already_existed = existing_book is not None
    
    if existing_book:
        logger.info(f"Book already exists in database: {existing_book.title}")
        book_to_return = existing_book
    else:
        # Fetch from Google Books API
        book_data = await google_books_service.get_book_by_id(google_book_id)
        if not book_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {google_book_id} not found in Google Books"
            )
        
        # Transform to BookCreate schema
        try:
            book_create = transform_to_book_create(book_data)
        except Exception as e:
            logger.error(f"Failed to transform book data: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process book data from Google Books"
            )
        
        # Save to database
        new_book = Book(**book_create.model_dump())
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
        
        logger.success(f"Added book from Google Books: {new_book.title} (ID: {new_book.id})")
        book_to_return = new_book
    
    # Create reading_progress entry for this user (idempotent)
    existing_progress = db.query(ReadingProgress).filter(
        ReadingProgress.userId == current_user.id,
        ReadingProgress.bookId == book_to_return.id
    ).first()
    
    if not existing_progress:
        reading_progress = ReadingProgress(
            userId=current_user.id,
            bookId=book_to_return.id,
            status="not_started",
            currentPage=0,
            progressPercentage=0.0
        )
        db.add(reading_progress)
        db.commit()
        logger.info(f"Created reading_progress for user {current_user.id} on book {book_to_return.id}")
    else:
        logger.info(f"Reading progress already exists for user {current_user.id} on book {book_to_return.id}")
    
    return book_to_return


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str,
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


@router.get("/{book_id}/related")
async def get_related_books(
    book_id: str,
    max_results: int = Query(6, ge=1, le=20, description="Maximum number of related books"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get related books based on the current book's author or similar title.
    Filters out the current book from results.
    
    Args:
        book_id: Book ID (Google Books ID)
        max_results: Maximum number of related books to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Related books from Google Books API
        
    Raises:
        HTTPException: If book not found
    """
    # First, get the current book details
    book = db.query(Book).filter(Book.id == book_id).first()
    
    if not book:
        # Try to fetch from Google Books API if not in local DB
        google_book = await google_books_service.get_book_by_id(book_id)
        if not google_book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        # Use data from Google Books
        author = google_book.get("author", "")
        title = google_book.get("title", "")
    else:
        author = book.author
        title = book.title
    
    # Search for books by the same author
    # Google Books API supports "inauthor:" prefix for author search
    search_query = f"inauthor:{author}" if author else f'intitle:"{title}"'
    
    # Search for related books
    related_books = await google_books_service.search_books(
        query=search_query,
        max_results=max_results + 5,  # Fetch more to account for filtering
        start_index=0
    )
    
    # Filter out the current book and limit results
    filtered_books = []
    for book_data in related_books:
        # Skip if it's the same book (by ID)
        if book_data.get("googleBooksId") == book_id:
            continue
        
        # Also skip if title is too similar (likely the same book)
        book_title = book_data.get("title", "").lower().strip()
        current_title = title.lower().strip()
        if book_title == current_title:
            continue
        
        filtered_books.append(book_data)
        
        # Stop once we have enough results
        if len(filtered_books) >= max_results:
            break
    
    logger.info(f"Found {len(filtered_books)} related books for book {book_id}")
    
    return {
        "book_id": book_id,
        "search_query": search_query,
        "total_results": len(filtered_books),
        "results": filtered_books
    }

