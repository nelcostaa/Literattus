"""
Club model - migrated from TypeORM Club entity.
Represents book clubs with member management.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Club(Base):
    """Club model for book club management."""

    __tablename__ = "clubs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Club information
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    coverImage = Column("cover_image", String(1000), nullable=True)

    # Privacy settings
    isPrivate = Column("is_private", Boolean, default=False, nullable=False)

    # Creator
    createdById = Column("created_by_id", Integer, ForeignKey("users.id"), nullable=False)

    # Settings
    maxMembers = Column("max_members", Integer, default=50, nullable=False)

    # Timestamps
    createdAt = Column("created_at", DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    createdBy = relationship("User", back_populates="createdClubs", foreign_keys=[createdById])
    members = relationship("ClubMember", back_populates="club", cascade="all, delete-orphan")
    discussions = relationship("Discussion", back_populates="club", cascade="all, delete-orphan")
    clubBooks = relationship("ClubBook", back_populates="club", cascade="all, delete-orphan")
    readingProgress = relationship("ReadingProgress", back_populates="club")

    def __repr__(self) -> str:
        return f"<Club(id={self.id}, name='{self.name}', members={len(self.members)})>"

    @property
    def member_count(self) -> int:
        """Get current member count."""
        return len(self.members) if self.members else 0

    @property
    def is_full(self) -> bool:
        """Check if club has reached maximum members."""
        return self.member_count >= self.maxMembers

