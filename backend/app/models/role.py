"""
Role Model
SQLAlchemy model for role-based access control and granular permission scopes
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin


class Role(Base, UUIDMixin, TimestampMixin):
    """
    Role model defining authorization roles and permission scopes.
    
    Default Roles:
    - admin: Full system access, management capabilities
    - investigator: Video upload, search, analytics, and report generation
    - viewer: Read-only access to assigned videos and search results
    """
    
    __tablename__ = "roles"
    
    # Role name (unique key identifier)
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="Unique role name identifier (admin, investigator, viewer)"
    )
    
    # Display name and description
    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Human-readable role name"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Detailed description of role responsibilities"
    )
    
    # Granular permissions stored as JSON object/list
    # e.g., {"videos": ["create", "read", "update", "delete"], "reports": ["create", "read"]}
    permissions: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="JSON dictionary of granular permission scopes"
    )
    
    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="role_rel",
        cascade="save-update, merge"
    )
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"
