"""Book-related Pydantic schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class BookBase(BaseModel):
    """Base book schema with common fields."""
    
    googleBooksId: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=500)
    isbn: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    coverImage: Optional[str] = Field(None, max_length=1000)
    publishedDate: Optional[str] = Field(None, max_length=50)
    pageCount: Optional[int] = Field(None, ge=1)
    genres: Optional[List[str]] = None
    averageRating: float = Field(default=0.0, ge=0.0, le=5.0)


class BookCreate(BookBase):
    """Schema for creating a new book."""
    pass


class BookUpdate(BaseModel):
    """Schema for updating book information."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    author: Optional[str] = Field(None, min_length=1, max_length=500)
    isbn: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    coverImage: Optional[str] = Field(None, max_length=1000)
    publishedDate: Optional[str] = Field(None, max_length=50)
    pageCount: Optional[int] = Field(None, ge=1)
    genres: Optional[List[str]] = None
    averageRating: Optional[float] = Field(None, ge=0.0, le=5.0)


class BookResponse(BookBase):
    """Schema for book response."""
    
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class BookSearch(BaseModel):
    """Schema for book search query."""
    
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=10, ge=1, le=40)
    start_index: int = Field(default=0, ge=0)

