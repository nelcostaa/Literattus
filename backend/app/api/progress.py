"""
Reading Progress API endpoints.
Handles user-specific reading progress tracking for books.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.book import Book
from app.models.reading_progress import ReadingProgress
from app.schemas.reading_progress import ReadingProgressResponse, ReadingProgressUpdate

router = APIRouter()


@router.get("/{book_id}", response_model=ReadingProgressResponse)
async def get_reading_progress(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get reading progress for a specific book for the current user.
    
    Args:
        book_id: Book ID (Google Books ID)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ReadingProgressResponse: Reading progress object
        
    Raises:
        HTTPException: If book not found or no reading progress exists
    """
    # Verify book exists
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Get reading progress for this user and book
    progress = db.query(ReadingProgress).filter(
        ReadingProgress.userId == current_user.id,
        ReadingProgress.bookId == book_id
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading progress not found for this book"
        )
    
    return progress


@router.put("/{book_id}", response_model=ReadingProgressResponse)
async def update_reading_progress(
    book_id: str,
    progress_data: ReadingProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update reading progress for a specific book.
    Automatically recalculates progressPercentage if currentPage is updated.
    Handles status transitions (e.g., 'not_started' -> 'reading', 'reading' -> 'completed').
    
    Args:
        book_id: Book ID (Google Books ID)
        progress_data: Updated progress data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ReadingProgressResponse: Updated reading progress object
        
    Raises:
        HTTPException: If book not found or no reading progress exists
    """
    # Verify book exists
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Get existing reading progress
    progress = db.query(ReadingProgress).filter(
        ReadingProgress.userId == current_user.id,
        ReadingProgress.bookId == book_id
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading progress not found for this book"
        )
    
    # Update status if provided
    if progress_data.status is not None:
        old_status = progress.status
        progress.status = progress_data.status
        
        # Handle status transitions
        if progress_data.status == "reading" and old_status == "not_started":
            if not progress.startedAt:
                progress.startedAt = datetime.utcnow()
        elif progress_data.status == "completed":
            if not progress.completedAt:
                progress.completedAt = datetime.utcnow()
            # Ensure progress is 100% when completed
            if book.pageCount and book.pageCount > 0:
                progress.currentPage = book.pageCount
                progress.progressPercentage = 100.0
        elif progress_data.status == "not_started":
            # Reset progress if going back to not_started
            progress.currentPage = 0
            progress.progressPercentage = 0.0
            progress.startedAt = None
            progress.completedAt = None
    
    # Update current page if provided
    if progress_data.currentPage is not None:
        if book.pageCount and book.pageCount > 0:
            # Clamp currentPage to valid range
            current_page = max(0, min(progress_data.currentPage, book.pageCount))
            progress.currentPage = current_page
            
            # Recalculate progress percentage
            progress.progressPercentage = round((current_page / book.pageCount) * 100, 2)
            
            # Auto-update status based on progress
            if progress.progressPercentage >= 100.0:
                progress.status = "completed"
                if not progress.completedAt:
                    progress.completedAt = datetime.utcnow()
            elif progress.progressPercentage > 0 and progress.status == "not_started":
                progress.status = "reading"
                if not progress.startedAt:
                    progress.startedAt = datetime.utcnow()
        else:
            # Book has no page count, just update the page number
            progress.currentPage = max(0, progress_data.currentPage)
            progress.progressPercentage = 0.0
    
    # Update manual progress percentage if provided (overrides page-based calculation)
    if progress_data.progressPercentage is not None:
        progress.progressPercentage = max(0.0, min(100.0, progress_data.progressPercentage))
        
        # Auto-update status based on progress
        if progress.progressPercentage >= 100.0:
            progress.status = "completed"
            if not progress.completedAt:
                progress.completedAt = datetime.utcnow()
        elif progress.progressPercentage > 0 and progress.status == "not_started":
            progress.status = "reading"
            if not progress.startedAt:
                progress.startedAt = datetime.utcnow()
    
    # Update rating if provided
    if progress_data.rating is not None:
        progress.rating = progress_data.rating
    
    # Update review if provided
    if progress_data.review is not None:
        progress.review = progress_data.review
    
    db.commit()
    db.refresh(progress)
    
    logger.info(f"Updated reading progress for user {current_user.id} on book {book_id}")
    return progress


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reading_progress(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete reading progress for a specific book (remove from catalog).
    This removes the user's reading progress record but does not delete the book itself.
    
    Args:
        book_id: Book ID (Google Books ID)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        None
        
    Raises:
        HTTPException: If book not found or no reading progress exists
    """
    # Verify book exists
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Get reading progress
    progress = db.query(ReadingProgress).filter(
        ReadingProgress.userId == current_user.id,
        ReadingProgress.bookId == book_id
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading progress not found for this book"
        )
    
    db.delete(progress)
    db.commit()
    
    logger.info(f"Deleted reading progress for user {current_user.id} on book {book_id}")
    return None

