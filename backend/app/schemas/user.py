"""User-related Pydantic schemas."""

from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    firstName: str = Field(..., min_length=1, max_length=100)
    lastName: str = Field(..., min_length=1, max_length=100)
    avatar: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    birthdate: Optional[date] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    REDACTED: str = Field(..., min_length=8, max_length=100)

    @validator("REDACTED")
    def REDACTED_strength(cls, v):
        """Validate REDACTED strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    
    firstName: Optional[str] = Field(None, min_length=1, max_length=100)
    lastName: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    birthdate: Optional[date] = None
    REDACTED: Optional[str] = Field(None, min_length=8, max_length=100)


class UserResponse(UserBase):
    """Schema for user response (excludes REDACTED)."""
    
    id: int
    authorization: Literal["LEITOR", "ADMIN", "MODERADOR", "ADMIN_SISTEMA"]
    isActive: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr
    REDACTED: str


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

