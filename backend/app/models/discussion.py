"""
Discussion model - migrated from TypeORM Discussion entity.
Represents discussion threads and comments within book clubs.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Discussion(Base):
    """Discussion model for club discussion threads and comments."""

    __tablename__ = "discussions"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign keys
    clubId = Column("club_id", Integer, ForeignKey("clubs.id"), nullable=False, index=True)
    userId = Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Optional parent discussion for nested comments/replies
    parentId = Column("parent_id", Integer, ForeignKey("discussions.id"), nullable=True, index=True)

    # Discussion content
    title = Column(String(300), nullable=True)  # Only for top-level discussions
    content = Column(Text, nullable=False)

    # Timestamps
    createdAt = Column("created_at", DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    club = relationship("Club", back_populates="discussions")
    user = relationship("User", back_populates="discussions")
    
    # Self-referential relationship for nested comments
    parent = relationship("Discussion", remote_side=[id], backref="replies")

    def __repr__(self) -> str:
        return f"<Discussion(id={self.id}, club_id={self.clubId}, user_id={self.userId}, title='{self.title}')>"

    @property
    def is_top_level(self) -> bool:
        """Check if this is a top-level discussion (not a reply)."""
        return self.parentId is None

    @property
    def is_reply(self) -> bool:
        """Check if this is a reply to another discussion."""
        return self.parentId is not None

    @property
    def reply_count(self) -> int:
        """Get number of replies to this discussion."""
        return len(self.replies) if hasattr(self, 'replies') else 0

