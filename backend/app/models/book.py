"""
Book model - migrated from TypeORM Book entity.
Represents books in the system with Google Books API integration.
Uses Google Books ID as primary key per database requirements.
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Date, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class Book(Base):
    """Book model for catalog management."""

    __tablename__ = "books"

    # Primary key - Google Books ID (max 12 characters per PDF spec)
    id = Column(String(12), primary_key=True, index=True)

    # Book information
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    coverImage = Column("cover_image", String(2048), nullable=True)
    isbn = Column(String(13), unique=True, nullable=True, index=True)
    publishedDate = Column("published_date", Date, nullable=True)
    pageCount = Column("page_count", Integer, nullable=True)

    # Timestamps
    createdAt = Column("created_at", DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    readingProgress = relationship("ReadingProgress", back_populates="book", cascade="all, delete-orphan")
    clubBooks = relationship("ClubBook", back_populates="book", cascade="all, delete-orphan")
    discussions = relationship("Discussion", back_populates="book", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title='{self.title}', author='{self.author}')>"

