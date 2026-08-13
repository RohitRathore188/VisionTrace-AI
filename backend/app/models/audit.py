"""
Audit Log Model
SQLAlchemy model for immutable security audit logging of user actions and evidence access
"""

import uuid
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """
    Immutable Audit Trail recording all security operations, logins, evidence accesses, searches, and exports.
    """
    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User ID who executed the action"
    )

    user_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="system@visiontrace.ai",
        index=True,
        comment="User email for fast audit queries"
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Operation name (e.g., USER_LOGIN, SEARCH_EXECUTE, CASE_CREATE, EVIDENCE_EXPORT)"
    )

    resource_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Target resource category (video, search, case, evidence, user)"
    )

    resource_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Identifier string of affected resource"
    )

    result_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="SUCCESS",
        comment="SUCCESS, FAILURE, DENIED"
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="127.0.0.1"
    )

    details_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Detailed action metadata"
    )

    def __repr__(self) -> str:
        return f"<AuditLog(action='{self.action}', user='{self.user_email}', resource='{self.resource_type}:{self.resource_id}')>"
