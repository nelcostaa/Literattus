"""ClubMember-related Pydantic schemas."""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class ClubMemberBase(BaseModel):
    """Base club member schema with common fields."""
    
    role: Literal["owner", "admin", "member"] = "member"


class ClubMemberCreate(BaseModel):
    """Schema for adding a member to a club."""
    
    userId: int
    clubId: int
    role: Literal["owner", "admin", "member"] = "member"


class ClubMemberUpdate(BaseModel):
    """Schema for updating club member role."""
    
    role: Literal["owner", "admin", "member"]


class ClubMemberResponse(ClubMemberBase):
    """Schema for club member response."""
    
    id: int
    userId: int
    clubId: int
    joinedAt: datetime
    user: Optional[UserResponse] = None  # Include user data if available

    class Config:
        from_attributes = True

