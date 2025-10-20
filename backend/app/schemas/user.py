"""User-related Pydantic schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr
    firstName: str = Field(..., min_length=1, max_length=100)
    lastName: str = Field(..., min_length=1, max_length=100)
    avatar: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    password: str = Field(..., min_length=8, max_length=100)

    @validator("password")
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    
    firstName: Optional[str] = Field(None, min_length=1, max_length=100)
    lastName: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar: Optional[str] = None
    bio: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserResponse(UserBase):
    """Schema for user response (excludes password)."""
    
    id: int
    isActive: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Schema for token payload data."""
    
    user_id: int
    email: str
    exp: Optional[datetime] = None

