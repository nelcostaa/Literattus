"""Book-related Pydantic schemas."""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class BookBase(BaseModel):
    """Base book schema with common fields."""
    
    id: str = Field(..., min_length=1, max_length=12, description="Google Books ID")
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    coverImage: Optional[str] = Field(None, max_length=2048)
    isbn: Optional[str] = Field(None, max_length=13)
    publishedDate: Optional[date] = None
    pageCount: Optional[int] = Field(None, ge=1)


class BookCreate(BookBase):
    """Schema for creating a new book."""
    pass


class BookUpdate(BaseModel):
    """Schema for updating book information."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    coverImage: Optional[str] = Field(None, max_length=2048)
    isbn: Optional[str] = Field(None, max_length=13)
    publishedDate: Optional[date] = None
    pageCount: Optional[int] = Field(None, ge=1)


class BookResponse(BookBase):
    """Schema for book response."""
    
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class BookSearch(BaseModel):
    """Schema for book search query."""
    
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=10, ge=1, le=40)
    start_index: int = Field(default=0, ge=0)

