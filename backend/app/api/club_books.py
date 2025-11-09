"""
Club Books API endpoints.
Handles club reading lists, book nominations, and voting.
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.club import Club
from app.models.club_member import ClubMember
from app.models.club_book import ClubBook
from app.models.book import Book
from app.schemas.club_book import ClubBookCreate, ClubBookUpdate, ClubBookResponse

router = APIRouter()


@router.get("/{club_id}/books", response_model=List[ClubBookResponse])
async def get_club_books(
    club_id: int,
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of books for a club (current, planned, completed, voted).
    
    Args:
        club_id: Club ID
        status_filter: Filter by status (current, planned, completed, voted)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[ClubBookResponse]: List of club books
        
    Raises:
        HTTPException: If club not found or user doesn't have access
    """
    club = db.query(Club).filter(Club.id == club_id).first()
    
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    
    # Check access for private clubs
    if club.isPrivate:
        is_member = db.query(ClubMember).filter(
            ClubMember.clubId == club_id,
            ClubMember.userId == current_user.id
        ).first()
        
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this private club"
            )
    
    # Build query
    query = db.query(ClubBook).filter(ClubBook.clubId == club_id)
    
    if status_filter:
        query = query.filter(ClubBook.status == status_filter)
    
    books = query.order_by(ClubBook.addedAt.desc()).all()
    
    return books


@router.post("/{club_id}/books/nominate", response_model=ClubBookResponse, status_code=status.HTTP_201_CREATED)
async def nominate_book(
    club_id: int,
    book_data: ClubBookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Nominate a book for the club (members only).
    Creates a club_book with status 'voted'.
    
    Args:
        club_id: Club ID
        book_data: Book nomination data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ClubBookResponse: Created club book object
        
    Raises:
        HTTPException: If club not found, user is not a member, or book already nominated
    """
    # Verify club exists
    club = db.query(Club).filter(Club.id == club_id).first()
    
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    
    # Verify user is a member
    membership = db.query(ClubMember).filter(
        ClubMember.clubId == club_id,
        ClubMember.userId == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a member to nominate books"
        )
    
    # Verify book exists
    book = db.query(Book).filter(Book.id == book_data.bookId).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Verify clubId in request matches URL parameter
    if book_data.clubId != club_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Club ID mismatch"
        )
    
    # Check if book already in this club
    existing = db.query(ClubBook).filter(
        ClubBook.clubId == club_id,
        ClubBook.bookId == book_data.bookId
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book already nominated or in club reading list"
        )
    
    # Create club book nomination with 'voted' status
    new_club_book = ClubBook(
        clubId=club_id,
        bookId=book_data.bookId,
        status="voted"  # Nominations start as 'voted'
    )
    
    db.add(new_club_book)
    db.commit()
    db.refresh(new_club_book)
    
    return new_club_book


@router.put("/{club_id}/books/{book_id}", response_model=ClubBookResponse)
async def update_club_book(
    club_id: int,
    book_id: str,
    book_data: ClubBookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a club book status (admin/owner only).
    Can change status from voted → planned → current → completed.
    
    Args:
        club_id: Club ID
        book_id: Book ID (Google Books ID)
        book_data: Updated book data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ClubBookResponse: Updated club book object
        
    Raises:
        HTTPException: If club not found, book not found, or user is not admin
    """
    club = db.query(Club).filter(Club.id == club_id).first()
    
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    
    # Check if user is admin/owner
    membership = db.query(ClubMember).filter(
        ClubMember.clubId == club_id,
        ClubMember.userId == current_user.id
    ).first()
    
    if not membership or membership.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update club books"
        )
    
    # Find club book
    club_book = db.query(ClubBook).filter(
        ClubBook.clubId == club_id,
        ClubBook.bookId == book_id
    ).first()
    
    if not club_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found in club reading list"
        )
    
    # Update status
    old_status = club_book.status
    club_book.status = book_data.status
    
    # Auto-update timestamps based on status changes
    if book_data.status == "current" and old_status != "current":
        club_book.startedAt = datetime.utcnow()
    elif book_data.status == "completed" and old_status != "completed":
        club_book.completedAt = datetime.utcnow()
    
    # Allow manual timestamp overrides
    if book_data.startedAt is not None:
        club_book.startedAt = book_data.startedAt
    if book_data.completedAt is not None:
        club_book.completedAt = book_data.completedAt
    
    db.commit()
    db.refresh(club_book)
    
    return club_book


@router.delete("/{club_id}/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_club_book(
    club_id: int,
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a book from club reading list (admin/owner only).
    
    Args:
        club_id: Club ID
        book_id: Book ID (Google Books ID)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        None
        
    Raises:
        HTTPException: If club not found, book not found, or user is not admin
    """
    club = db.query(Club).filter(Club.id == club_id).first()
    
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    
    # Check if user is admin/owner
    membership = db.query(ClubMember).filter(
        ClubMember.clubId == club_id,
        ClubMember.userId == current_user.id
    ).first()
    
    if not membership or membership.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to remove club books"
        )
    
    # Find club book
    club_book = db.query(ClubBook).filter(
        ClubBook.clubId == club_id,
        ClubBook.bookId == book_id
    ).first()
    
    if not club_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found in club reading list"
        )
    
    db.delete(club_book)
    db.commit()
    
    return None


@router.get("/{club_id}/books/current", response_model=ClubBookResponse)
async def get_current_club_book(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the current book being read by the club.
    
    Args:
        club_id: Club ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ClubBookResponse: Current club book
        
    Raises:
        HTTPException: If club not found, no current book, or user doesn't have access
    """
    club = db.query(Club).filter(Club.id == club_id).first()
    
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    
    # Check access for private clubs
    if club.isPrivate:
        is_member = db.query(ClubMember).filter(
            ClubMember.clubId == club_id,
            ClubMember.userId == current_user.id
        ).first()
        
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this private club"
            )
    
    # Get current book
    current_book = db.query(ClubBook).filter(
        ClubBook.clubId == club_id,
        ClubBook.status == "current"
    ).first()
    
    if not current_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club has no current book"
        )
    
    return current_book

