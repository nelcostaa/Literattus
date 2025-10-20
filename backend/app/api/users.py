"""
Users API endpoints.
Handles user profile management and user-related operations.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_REDACTED_hash
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of users (paginated).
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[UserResponse]: List of users
    """
    users = db.query(User).filter(User.isActive == True).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        UserResponse: User object
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id, User.isActive == True).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's profile.
    
    Args:
        user_data: Updated user data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Updated user object
    """
    # Update fields if provided
    if user_data.firstName is not None:
        current_user.firstName = user_data.firstName
    if user_data.lastName is not None:
        current_user.lastName = user_data.lastName
    if user_data.avatar is not None:
        current_user.avatar = user_data.avatar
    if user_data.bio is not None:
        current_user.bio = user_data.bio
    if user_data.REDACTED is not None:
        current_user.REDACTED = get_REDACTED_hash(user_data.REDACTED)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete (deactivate) current user's account.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        None
    """
    # Soft delete by marking as inactive
    current_user.isActive = False
    db.commit()
    
    return None

