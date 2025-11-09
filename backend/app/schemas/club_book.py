"""ClubBook-related Pydantic schemas."""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ClubBookBase(BaseModel):
    """Base club book schema with common fields."""
    
    status: Literal["planned", "current", "completed", "voted"] = "planned"


class ClubBookCreate(BaseModel):
    """Schema for adding a book to a club."""
    
    clubId: int
    bookId: str = Field(..., min_length=1, max_length=12)
    status: Literal["planned", "current", "completed", "voted"] = "planned"


class ClubBookUpdate(BaseModel):
    """Schema for updating club book status."""
    
    status: Literal["planned", "current", "completed", "voted"]
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None


class ClubBookResponse(ClubBookBase):
    """Schema for club book response."""
    
    id: int
    clubId: int
    bookId: str
    addedAt: datetime
    startedAt: Optional[datetime]
    completedAt: Optional[datetime]

    class Config:
        from_attributes = True

