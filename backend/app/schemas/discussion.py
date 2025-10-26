"""Discussion-related Pydantic schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DiscussionBase(BaseModel):
    """Base discussion schema with common fields."""
    
    content: str = Field(..., min_length=1)
    title: Optional[str] = Field(None, max_length=300)


class DiscussionCreate(DiscussionBase):
    """Schema for creating a new discussion."""
    
    clubId: int
    bookId: str = Field(..., min_length=1, max_length=12, description="Google Books ID")
    parentId: Optional[int] = None  # For replies


class DiscussionUpdate(BaseModel):
    """Schema for updating discussion."""
    
    content: Optional[str] = Field(None, min_length=1)
    title: Optional[str] = Field(None, max_length=300)


class DiscussionResponse(DiscussionBase):
    """Schema for discussion response."""
    
    id: int
    clubId: int
    userId: int
    bookId: str
    parentId: Optional[int]
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

