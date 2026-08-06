"""
Report Model
SQLAlchemy model for investigative intelligence reports, bookmarks, and evidence export
"""

import enum
import uuid
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Text, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user import User


class ReportStatus(str, enum.Enum):
    """Lifecycle status of generated intelligence report"""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Report(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Report model storing generated intelligence briefings, compiled video evidence, and exported PDF artifacts.
    """
    
    __tablename__ = "reports"
    
    # Foreign Key to author user
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID who created or owns the investigation report"
    )
    
    # Report Identification & Description
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Title of the investigative report"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Executive summary or case background notes"
    )
    
    report_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="investigation",
        index=True,
        comment="Type of report (e.g., investigation, security_audit, object_summary)"
    )
    
    # Lifecycle Status
    status: Mapped[ReportStatus] = mapped_column(
        SQLEnum(ReportStatus, name="reportstatus"),
        nullable=False,
        default=ReportStatus.DRAFT,
        index=True,
        comment="Report lifecycle status (draft, generating, completed, archived)"
    )
    
    # Report Content & Evidence Payload (JSON schema containing frames, object IDs, notes)
    content: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="JSON document containing matched clip IDs, timeline events, and notes"
    )
    
    # Exported artifact location (PDF, HTML, ZIP bundle)
    file_path: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="Path or URL to exported report artifact (PDF/HTML)"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="reports"
    )
    
    def __repr__(self) -> str:
        return f"<Report(id={self.id}, title='{self.title}', status='{self.status.value}')>"
