"""
Evidence Model
SQLAlchemy model for SHA-256 verified forensic evidence items, clips, and keyframes
"""

import enum
import uuid
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Text, Float, Integer, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.video import Video
    from app.models.user import User


class IntegrityStatus(str, enum.Enum):
    VERIFIED = "verified"
    MODIFIED = "modified"
    UNKNOWN = "unknown"


class EvidenceItem(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Forensic Evidence Item with cryptographic SHA-256 hashing and case linking.
    """
    __tablename__ = "evidence_items"

    evidence_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique evidence tag (e.g. EVI-2026-9901)"
    )

    case_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("cases.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    video_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    frame_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("frames.id", ondelete="SET NULL"),
        nullable=True
    )

    object_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("objects.id", ondelete="SET NULL"),
        nullable=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Evidence item title"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="Cryptographic SHA-256 hash of evidence file"
    )

    file_path: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        comment="Storage file path"
    )

    file_size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    timestamp_seconds: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0
    )

    integrity_status: Mapped[IntegrityStatus] = mapped_column(
        SQLEnum(IntegrityStatus, name="integritystatus"),
        nullable=False,
        default=IntegrityStatus.VERIFIED,
        index=True
    )

    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    metadata_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict
    )

    def __repr__(self) -> str:
        return f"<EvidenceItem(evidence_id='{self.evidence_id}', hash='{self.sha256_hash[:10]}...', integrity='{self.integrity_status.value}')>"
