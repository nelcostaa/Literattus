"""
ClubMember model - migrated from TypeORM ClubMember entity.
Represents membership relationship between users and clubs with roles.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class ClubMember(Base):
    """ClubMember model for managing book club memberships."""

    __tablename__ = "club_members"

    # Composite unique constraint on user_id + club_id
    __table_args__ = (
        UniqueConstraint("user_id", "club_id", name="uq_user_club"),
    )

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign keys
    userId = Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True)
    clubId = Column("club_id", Integer, ForeignKey("clubs.id"), nullable=False, index=True)

    # Role: 'owner', 'admin', 'member'
    role = Column(String(50), default="member", nullable=False)

    # Timestamps
    joinedAt = Column("joined_at", DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="clubMemberships")
    club = relationship("Club", back_populates="members")

    def __repr__(self) -> str:
        return f"<ClubMember(id={self.id}, user_id={self.userId}, club_id={self.clubId}, role='{self.role}')>"

    @property
    def is_owner(self) -> bool:
        """Check if member is club owner."""
        return self.role == "owner"

    @property
    def is_admin(self) -> bool:
        """Check if member is club admin."""
        return self.role in ["owner", "admin"]

    @property
    def can_manage_club(self) -> bool:
        """Check if member can manage club settings."""
        return self.is_admin

