"""ReadingProgress-related Pydantic schemas."""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ReadingProgressBase(BaseModel):
    """Base reading progress schema with common fields."""
    
    status: Literal["not_started", "reading", "completed", "abandoned"] = "not_started"
    currentPage: int = Field(default=0, ge=0)
    progressPercentage: float = Field(default=0.0, ge=0.0, le=100.0)
    rating: Optional[int] = Field(None, ge=1, le=5)
    review: Optional[str] = Field(None, max_length=2000)


class ReadingProgressCreate(BaseModel):
    """Schema for creating reading progress."""
    
    userId: int
    bookId: str = Field(..., min_length=1, max_length=12, description="Google Books ID")
    clubId: Optional[int] = None
    status: Literal["not_started", "reading", "completed", "abandoned"] = "not_started"
    currentPage: int = Field(default=0, ge=0)


class ReadingProgressUpdate(BaseModel):
    """Schema for updating reading progress."""
    
    status: Optional[Literal["not_started", "reading", "completed", "abandoned"]] = None
    currentPage: Optional[int] = Field(None, ge=0)
    progressPercentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    rating: Optional[int] = Field(None, ge=1, le=5)
    review: Optional[str] = Field(None, max_length=2000)


class ReadingProgressResponse(ReadingProgressBase):
    """Schema for reading progress response."""
    
    id: int
    userId: int
    bookId: str
    clubId: Optional[int]
    startedAt: Optional[datetime]
    completedAt: Optional[datetime]
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

