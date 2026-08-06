"""
Video Model
SQLAlchemy model for uploaded video assets and ingestion metadata
"""

import enum
import uuid
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Text, Float, BigInteger, Integer, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.frame import Frame
    from app.models.object import ObjectDetection


class VideoStatus(str, enum.Enum):
    """Processing status for ingested videos"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Video(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Video model representing surveillance or uploaded video files.
    """
    
    __tablename__ = "videos"
    
    # Foreign Key to uploader user
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID who uploaded the video"
    )
    
    # Metadata
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Human-readable title or camera identifier"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Detailed description or notes"
    )
    
    # File Storage attributes
    file_path: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        comment="Relative path or cloud URL storing the video file"
    )
    
    file_size_bytes: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Size of the video file in bytes"
    )
    
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="video/mp4",
        comment="MIME format of the video (e.g., video/mp4, video/avi)"
    )
    
    # Media Technical Characteristics
    duration_seconds: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Video total duration in seconds"
    )
    
    fps: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Frames per second"
    )
    
    width: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Video frame width in pixels"
    )
    
    height: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Video frame height in pixels"
    )
    
    total_frames: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Total frame count in video"
    )
    
    # Processing Status
    status: Mapped[VideoStatus] = mapped_column(
        SQLEnum(VideoStatus, name="videostatus"),
        nullable=False,
        default=VideoStatus.PENDING,
        index=True,
        comment="Ingestion & AI pipeline status (pending, processing, completed, failed)"
    )
    
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if pipeline processing failed"
    )
    
    # Extensible JSON metadata
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="JSON payload for custom attributes, camera location, or ingestion logs"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="videos"
    )
    
    frames: Mapped[List["Frame"]] = relationship(
        "Frame",
        back_populates="video",
        cascade="all, delete-orphan"
    )
    
    objects: Mapped[List["ObjectDetection"]] = relationship(
        "ObjectDetection",
        back_populates="video",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Video(id={self.id}, title='{self.title}', status='{self.status.value}')>"
