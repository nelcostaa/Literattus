"""
Discussions API endpoints.
Handles club discussion threads and replies.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.club import Club
from app.models.club_member import ClubMember
from app.models.discussion import Discussion
from app.models.book import Book
from app.schemas.discussion import DiscussionCreate, DiscussionUpdate, DiscussionResponse

router = APIRouter()


@router.get("/{club_id}/discussions", response_model=List[DiscussionResponse])
async def get_club_discussions(
    club_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of discussions for a club.
    
    Args:
        club_id: Club ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[DiscussionResponse]: List of discussions
        
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
    
    # Get top-level discussions only (parentId is None)
    discussions = db.query(Discussion).filter(
        Discussion.clubId == club_id,
        Discussion.parentId == None
    ).order_by(Discussion.createdAt.desc()).offset(skip).limit(limit).all()
    
    return discussions


@router.post("/{club_id}/discussions", response_model=DiscussionResponse, status_code=status.HTTP_201_CREATED)
async def create_discussion(
    club_id: int,
    discussion_data: DiscussionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new discussion in a club.
    
    Args:
        club_id: Club ID
        discussion_data: Discussion creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        DiscussionResponse: Created discussion object
        
    Raises:
        HTTPException: If club not found, user is not a member, or book not found
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
            detail="You must be a member to create discussions"
        )
    
    # Verify book exists
    book = db.query(Book).filter(Book.id == discussion_data.bookId).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Verify clubId in request matches URL parameter
    if discussion_data.clubId != club_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Club ID mismatch"
        )
    
    # Create discussion
    new_discussion = Discussion(
        clubId=club_id,
        userId=current_user.id,
        bookId=discussion_data.bookId,
        parentId=discussion_data.parentId,
        title=discussion_data.title,
        content=discussion_data.content
    )
    
    db.add(new_discussion)
    db.commit()
    db.refresh(new_discussion)
    
    return new_discussion


@router.get("/discussions/{discussion_id}", response_model=DiscussionResponse)
async def get_discussion(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific discussion by ID.
    
    Args:
        discussion_id: Discussion ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        DiscussionResponse: Discussion object
        
    Raises:
        HTTPException: If discussion not found or user doesn't have access
    """
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    
    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion not found"
        )
    
    # Check access for private club discussions
    club = db.query(Club).filter(Club.id == discussion.clubId).first()
    
    if club and club.isPrivate:
        is_member = db.query(ClubMember).filter(
            ClubMember.clubId == discussion.clubId,
            ClubMember.userId == current_user.id
        ).first()
        
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this discussion"
            )
    
    return discussion


@router.put("/discussions/{discussion_id}", response_model=DiscussionResponse)
async def update_discussion(
    discussion_id: int,
    discussion_data: DiscussionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a discussion (author only).
    
    Args:
        discussion_id: Discussion ID
        discussion_data: Updated discussion data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        DiscussionResponse: Updated discussion object
        
    Raises:
        HTTPException: If discussion not found or user is not the author
    """
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    
    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion not found"
        )
    
    # Check if user is the author
    if discussion.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own discussions"
        )
    
    # Update fields if provided
    if discussion_data.content is not None:
        discussion.content = discussion_data.content
    if discussion_data.title is not None:
        discussion.title = discussion_data.title
    
    db.commit()
    db.refresh(discussion)
    
    return discussion


@router.delete("/discussions/{discussion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discussion(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a discussion (author or club admin only).
    
    Args:
        discussion_id: Discussion ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        None
        
    Raises:
        HTTPException: If discussion not found or user doesn't have permission
    """
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    
    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion not found"
        )
    
    # Check if user is the author or club admin
    is_author = discussion.userId == current_user.id
    
    membership = db.query(ClubMember).filter(
        ClubMember.clubId == discussion.clubId,
        ClubMember.userId == current_user.id
    ).first()
    
    is_admin = membership and membership.role in ["owner", "admin"]
    
    if not (is_author or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this discussion"
        )
    
    db.delete(discussion)
    db.commit()
    
    return None


@router.get("/discussions/{discussion_id}/replies", response_model=List[DiscussionResponse])
async def get_discussion_replies(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all replies to a discussion.
    
    Args:
        discussion_id: Parent discussion ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[DiscussionResponse]: List of reply discussions
        
    Raises:
        HTTPException: If discussion not found or user doesn't have access
    """
    # Verify parent discussion exists
    parent = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion not found"
        )
    
    # Check access for private club discussions
    club = db.query(Club).filter(Club.id == parent.clubId).first()
    
    if club and club.isPrivate:
        is_member = db.query(ClubMember).filter(
            ClubMember.clubId == parent.clubId,
            ClubMember.userId == current_user.id
        ).first()
        
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this discussion"
            )
    
    # Get all replies
    replies = db.query(Discussion).filter(
        Discussion.parentId == discussion_id
    ).order_by(Discussion.createdAt.asc()).all()
    
    return replies

