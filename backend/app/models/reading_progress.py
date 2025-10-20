"""
ReadingProgress model - migrated from TypeORM ReadingProgress entity.
Tracks user's reading progress for individual books.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class ReadingProgress(Base):
    """ReadingProgress model for tracking user's reading activity."""

    __tablename__ = "reading_progress"

    # Composite unique constraint on user_id + book_id
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="uq_user_book_progress"),
    )

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign keys
    userId = Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True)
    bookId = Column("book_id", Integer, ForeignKey("books.id"), nullable=False, index=True)

    # Progress tracking
    status = Column(String(50), default="not_started", nullable=False)  # not_started, reading, completed, abandoned
    currentPage = Column("current_page", Integer, default=0, nullable=False)
    progressPercentage = Column("progress_percentage", Float, default=0.0, nullable=False)

    # User rating (1-5 stars)
    rating = Column(Integer, nullable=True)

    # User review
    review = Column(String(2000), nullable=True)

    # Timestamps
    startedAt = Column("started_at", DateTime, nullable=True)
    completedAt = Column("completed_at", DateTime, nullable=True)
    createdAt = Column("created_at", DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="readingProgress")
    book = relationship("Book", back_populates="readingProgress")

    def __repr__(self) -> str:
        return f"<ReadingProgress(id={self.id}, user_id={self.userId}, book_id={self.bookId}, status='{self.status}', progress={self.progressPercentage}%)>"

    @property
    def is_completed(self) -> bool:
        """Check if book is completed."""
        return self.status == "completed"

    @property
    def is_reading(self) -> bool:
        """Check if currently reading."""
        return self.status == "reading"

    def update_progress(self, current_page: int, total_pages: int) -> None:
        """Update reading progress based on current page."""
        self.currentPage = current_page
        if total_pages > 0:
            self.progressPercentage = round((current_page / total_pages) * 100, 2)
        
        # Auto-update status
        if self.progressPercentage >= 100:
            self.status = "completed"
            if not self.completedAt:
                self.completedAt = datetime.utcnow()
        elif self.progressPercentage > 0 and self.status == "not_started":
            self.status = "reading"
            if not self.startedAt:
                self.startedAt = datetime.utcnow()

