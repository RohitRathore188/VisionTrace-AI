"""
Case Model
SQLAlchemy model for security incident investigation cases (e.g. INV-2026-00124)
"""

import enum
import uuid
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlalchemy import String, Text, Enum as SQLEnum, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user import User


class CaseStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    PENDING_REVIEW = "pending_review"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CasePriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Case(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Incident Case Model tracking investigations, evidence packages, and case notes.
    """
    __tablename__ = "cases"

    case_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique identifier string (e.g. INV-2026-00101)"
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Case title description"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Detailed incident report narrative"
    )

    status: Mapped[CaseStatus] = mapped_column(
        SQLEnum(CaseStatus, name="casestatus"),
        nullable=False,
        default=CaseStatus.OPEN,
        index=True
    )

    priority: Mapped[CasePriority] = mapped_column(
        SQLEnum(CasePriority, name="casepriority"),
        nullable=False,
        default=CasePriority.MEDIUM,
        index=True
    )

    assigned_investigator_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    notes_json: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        comment="Structured case notes and investigator timeline entries"
    )

    def __repr__(self) -> str:
        return f"<Case(case_number='{self.case_number}', status='{self.status.value}', priority='{self.priority.value}')>"
