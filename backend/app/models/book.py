"""
Book model - migrated from TypeORM Book entity.
Represents books in the system with Google Books API integration.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class Book(Base):
    """Book model for catalog management."""

    __tablename__ = "books"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Google Books integration
    googleBooksId = Column("google_books_id", String(255), unique=True, nullable=False, index=True)

    # Book information
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(500), nullable=False)
    isbn = Column(String(20), nullable=True, index=True)
    description = Column(Text, nullable=True)
    coverImage = Column("cover_image", String(1000), nullable=True)
    publishedDate = Column("published_date", String(50), nullable=True)
    pageCount = Column("page_count", Integer, nullable=True)

    # Genres stored as comma-separated string (simple-array equivalent)
    genres = Column(Text, nullable=True)  # Will store as JSON or comma-separated

    # Rating
    averageRating = Column("average_rating", Float, default=0.0, nullable=False)

    # Timestamps
    createdAt = Column("created_at", DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    readingProgress = relationship("ReadingProgress", back_populates="book", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title='{self.title}', author='{self.author}')>"

    @property
    def genres_list(self) -> list:
        """Get genres as a list."""
        if self.genres:
            return [g.strip() for g in self.genres.split(",")]
        return []

    @genres_list.setter
    def genres_list(self, value: list):
        """Set genres from a list."""
        if value:
            self.genres = ",".join(value)
        else:
            self.genres = None

