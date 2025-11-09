"""
User model - migrated from TypeORM User entity.
Represents application users with authentication and profile information.
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserAuthorization(str, enum.Enum):
    """User authorization levels."""
    LEITOR = "LEITOR"  # Standard reader
    ADMIN = "ADMIN"  # Club administrator
    MODERADOR = "MODERADOR"  # System moderator
    ADMIN_SISTEMA = "ADMIN_SISTEMA"  # System administrator


class User(Base):
    """User model for authentication and profile management."""

    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    REDACTED = Column(String(255), nullable=False)  # Hashed REDACTED

    # Profile fields
    firstName = Column("first_name", String(100), nullable=False)
    lastName = Column("last_name", String(100), nullable=False)
    avatar = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    phone = Column(String(20), unique=True, nullable=True)
    birthdate = Column(Date, nullable=True)

    # Authorization level
    authorization = Column(Enum(UserAuthorization), default=UserAuthorization.LEITOR, nullable=False)

    # Status
    isActive = Column("is_active", Boolean, default=True, nullable=False)

    # Timestamps
    createdAt = Column("created_at", DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    clubMemberships = relationship("ClubMember", back_populates="user", cascade="all, delete-orphan")
    readingProgress = relationship("ReadingProgress", back_populates="user", cascade="all, delete-orphan")
    discussions = relationship("Discussion", back_populates="user", cascade="all, delete-orphan")
    createdClubs = relationship("Club", back_populates="createdBy", foreign_keys="Club.createdById")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', name='{self.firstName} {self.lastName}')>"

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.firstName} {self.lastName}"

