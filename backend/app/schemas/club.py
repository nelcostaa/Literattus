"""Club-related Pydantic schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ClubBase(BaseModel):
    """Base club schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    coverImage: Optional[str] = Field(None, max_length=1000)
    isPrivate: bool = False
    maxMembers: int = Field(default=50, ge=2, le=1000)


class ClubCreate(ClubBase):
    """Schema for creating a new club."""
    pass


class ClubUpdate(BaseModel):
    """Schema for updating club information."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    coverImage: Optional[str] = Field(None, max_length=1000)
    isPrivate: Optional[bool] = None
    maxMembers: Optional[int] = Field(None, ge=2, le=1000)


class ClubResponse(ClubBase):
    """Schema for club response."""
    
    id: int
    createdById: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

