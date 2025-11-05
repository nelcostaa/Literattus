"""
Clubs API endpoints.
Handles book club management, memberships, and discussions.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.club import Club
from app.models.club_member import ClubMember
from app.schemas.club import ClubCreate, ClubUpdate, ClubResponse
from app.schemas.club_member import ClubMemberCreate, ClubMemberResponse

router = APIRouter()


@router.get("/", response_model=List[ClubResponse])
async def get_clubs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of clubs (shows only public clubs unless user is a member).
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[ClubResponse]: List of clubs
    """
    # Show public clubs and clubs the user is a member of
    clubs = db.query(Club).filter(
        (Club.isPrivate == False) | 
        (Club.members.any(ClubMember.userId == current_user.id))
    ).offset(skip).limit(limit).all()
    
    return clubs


@router.get("/my-clubs", response_model=List[ClubResponse])
async def get_my_clubs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get clubs the current user is a member of.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[ClubResponse]: List of user's clubs
    """
    memberships = db.query(ClubMember).filter(
        ClubMember.userId == current_user.id
    ).all()
    
    clubs = [membership.club for membership in memberships]
    return clubs


@router.get("/{club_id}", response_model=ClubResponse)
async def get_club(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get club by ID.
    
    Args:
        club_id: Club ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ClubResponse: Club object
        
    Raises:
        HTTPException: If club not found or user doesn't have access
    """
    club = db.query(Club).filter(Club.id == club_id).first()
    
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    
    # Check if user has access to private club
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
    
    return club


@router.post("/", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
async def create_club(
    club_data: ClubCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new book club.
    
    Args:
        club_data: Club creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ClubResponse: Created club object
    """
    # Create new club
    new_club = Club(
        name=club_data.name,
        description=club_data.description,
        coverImage=club_data.coverImage,
        isPrivate=club_data.isPrivate,
        maxMembers=club_data.maxMembers,
        createdById=current_user.id
    )
    
    db.add(new_club)
    db.flush()  # Get club ID before creating membership
    
    # Add creator as owner
    owner_membership = ClubMember(
        userId=current_user.id,
        clubId=new_club.id,
        role="owner"
    )
    
    db.add(owner_membership)
    db.commit()
    db.refresh(new_club)
    
    return new_club


@router.put("/{club_id}", response_model=ClubResponse)
async def update_club(
    club_id: int,
    club_data: ClubUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update club information (admin/owner only).
    
    Args:
        club_id: Club ID
        club_data: Updated club data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ClubResponse: Updated club object
        
    Raises:
        HTTPException: If club not found or user is not admin
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
            detail="You don't have permission to update this club"
        )
    
    # Update fields if provided
    if club_data.name is not None:
        club.name = club_data.name
    if club_data.description is not None:
        club.description = club_data.description
    if club_data.coverImage is not None:
        club.coverImage = club_data.coverImage
    if club_data.isPrivate is not None:
        club.isPrivate = club_data.isPrivate
    if club_data.maxMembers is not None:
        club.maxMembers = club_data.maxMembers
    
    db.commit()
    db.refresh(club)
    
    return club


@router.delete("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_club(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a club (owner only).
    
    Args:
        club_id: Club ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        None
        
    Raises:
        HTTPException: If club not found or user is not owner
    """
    club = db.query(Club).filter(Club.id == club_id).first()
    
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    
    # Check if user is owner
    membership = db.query(ClubMember).filter(
        ClubMember.clubId == club_id,
        ClubMember.userId == current_user.id,
        ClubMember.role == "owner"
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the club owner can delete the club"
        )
    
    db.delete(club)
    db.commit()
    
    return None


@router.post("/{club_id}/join", response_model=ClubMemberResponse, status_code=status.HTTP_201_CREATED)
async def join_club(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Join a book club.
    
    Args:
        club_id: Club ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ClubMemberResponse: Created membership object
        
    Raises:
        HTTPException: If club not found, full, or user already a member
    """
    club = db.query(Club).filter(Club.id == club_id).first()
    
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    
    # Check if already a member
    existing_membership = db.query(ClubMember).filter(
        ClubMember.clubId == club_id,
        ClubMember.userId == current_user.id
    ).first()
    
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this club"
        )
    
    # Check if club is full
    current_members = db.query(ClubMember).filter(ClubMember.clubId == club_id).count()
    if current_members >= club.maxMembers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Club has reached maximum members"
        )
    
    # Create membership
    new_membership = ClubMember(
        userId=current_user.id,
        clubId=club_id,
        role="member"
    )
    
    db.add(new_membership)
    db.commit()
    db.refresh(new_membership)
    
    return new_membership


@router.post("/{club_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_club(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Leave a book club.
    
    Args:
        club_id: Club ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        None
        
    Raises:
        HTTPException: If not a member or is the owner
    """
    membership = db.query(ClubMember).filter(
        ClubMember.clubId == club_id,
        ClubMember.userId == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a member of this club"
        )
    
    if membership.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Club owner cannot leave the club. Transfer ownership or delete the club."
        )
    
    db.delete(membership)
    db.commit()
    
    return None


@router.get("/{club_id}/members", response_model=List[ClubMemberResponse])
async def get_club_members(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of club members.
    
    Args:
        club_id: Club ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[ClubMemberResponse]: List of club members
        
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
    
    # Eagerly load user relationship
    from sqlalchemy.orm import joinedload
    members = db.query(ClubMember).options(
        joinedload(ClubMember.user)
    ).filter(ClubMember.clubId == club_id).all()
    return members

