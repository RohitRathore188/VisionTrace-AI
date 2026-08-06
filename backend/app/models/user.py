"""
User Model
SQLAlchemy model for user authentication, authorization, and profile management
"""

import enum
import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.video import Video
    from app.models.search_history import SearchHistory
    from app.models.report import Report


class UserRole(str, enum.Enum):
    """User roles for role-based access control"""
    ADMIN = "admin"
    INVESTIGATOR = "investigator"
    VIEWER = "viewer"


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    User model for authentication and authorization.
    
    Roles:
    - Admin: Full system access, user management, system configuration
    - Investigator: Can upload videos, search, create reports
    - Viewer: Read-only access to videos and search results
    """
    
    __tablename__ = "users"
    
    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="User email address (unique identifier)"
    )
    
    # Supabase user ID (maps to auth.users in Supabase)
    supabase_user_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
        comment="Supabase auth user ID"
    )
    
    # Profile
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="User's full name"
    )
    
    # Legacy role enum field for backward compatibility
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="userrole"),
        nullable=False,
        default=UserRole.VIEWER,
        comment="User role enum for access control"
    )
    
    # Foreign Key to roles table
    role_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Foreign key referencing roles.id"
    )
    
    # Account status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Account active status"
    )
    
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Email verification status"
    )
    
    # Login tracking
    last_login_at: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Last login timestamp (ISO format)"
    )
    
    # Relationships
    role_rel: Mapped[Optional["Role"]] = relationship(
        "Role",
        back_populates="users"
    )
    
    videos: Mapped[List["Video"]] = relationship(
        "Video",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    search_histories: Mapped[List["SearchHistory"]] = relationship(
        "SearchHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    reports: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_investigator(self) -> bool:
        """Check if user has investigator role"""
        return self.role == UserRole.INVESTIGATOR
    
    @property
    def is_viewer(self) -> bool:
        """Check if user has viewer role"""
        return self.role == UserRole.VIEWER
    
    @property
    def can_upload_videos(self) -> bool:
        """Check if user can upload videos"""
        return self.role in [UserRole.ADMIN, UserRole.INVESTIGATOR]
    
    @property
    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return self.role == UserRole.ADMIN
    
    @property
    def can_view_all_videos(self) -> bool:
        """Check if user can view all videos"""
        return self.role == UserRole.ADMIN
