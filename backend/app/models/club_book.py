"""
ClubBook model - Junction table for club-book relationships.
Represents which books are being read/discussed in each club.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class ClubBook(Base):
    """ClubBook model for managing club reading lists and book selections."""

    __tablename__ = "club_books"

    # Composite unique constraint on club_id + book_id
    __table_args__ = (
        UniqueConstraint("club_id", "book_id", name="uq_club_book"),
    )

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign keys
    clubId = Column("club_id", Integer, ForeignKey("clubs.id"), nullable=False, index=True)
    bookId = Column("book_id", String(12), ForeignKey("books.id"), nullable=False, index=True)

    # Status of book in club ('current', 'completed', 'planned', 'voted')
    status = Column(String(50), default="planned", nullable=False)

    # Timestamps
    addedAt = Column("added_at", DateTime, default=datetime.utcnow, nullable=False)
    startedAt = Column("started_at", DateTime, nullable=True)
    completedAt = Column("completed_at", DateTime, nullable=True)

    # Relationships
    club = relationship("Club", back_populates="clubBooks")
    book = relationship("Book", back_populates="clubBooks")

    def __repr__(self) -> str:
        return f"<ClubBook(id={self.id}, club_id={self.clubId}, book_id={self.bookId}, status='{self.status}')>"

    @property
    def is_current(self) -> bool:
        """Check if this is the club's current book."""
        return self.status == "current"

    @property
    def is_completed(self) -> bool:
        """Check if club has completed this book."""
        return self.status == "completed"

