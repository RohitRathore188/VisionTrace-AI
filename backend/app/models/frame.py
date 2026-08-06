"""
Frame Model
SQLAlchemy model for extracted video frames and sampling keyframes
"""

import uuid
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Float, Integer, ForeignKey, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.video import Video
    from app.models.object import ObjectDetection
    from app.models.embedding import Embedding


class Frame(Base, UUIDMixin, TimestampMixin):
    """
    Frame model representing sampled keyframes extracted from video processing.
    """
    
    __tablename__ = "frames"
    
    # Foreign Key to parent video
    video_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key referencing parent video ID"
    )
    
    # Frame Identifiers
    frame_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Zero-based sequence number of the frame within the video"
    )
    
    timestamp_seconds: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Exact timestamp in seconds from video start"
    )
    
    # Frame storage reference
    image_path: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        comment="Path or URL storing extracted frame image asset"
    )
    
    # Pixel dimensions
    width: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Frame width in pixels"
    )
    
    height: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Frame height in pixels"
    )
    
    # Additional keyframe metadata
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="JSON dictionary storing sampling rate, blur metrics, or lighting condition"
    )
    
    # Relationships
    video: Mapped["Video"] = relationship(
        "Video",
        back_populates="frames"
    )
    
    objects: Mapped[List["ObjectDetection"]] = relationship(
        "ObjectDetection",
        back_populates="frame",
        cascade="all, delete-orphan"
    )
    
    embeddings: Mapped[List["Embedding"]] = relationship(
        "Embedding",
        back_populates="frame",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("ix_frames_video_timestamp", "video_id", "timestamp_seconds"),
        Index("ix_frames_video_frame_number", "video_id", "frame_number"),
    )
    
    def __repr__(self) -> str:
        return f"<Frame(id={self.id}, video_id={self.video_id}, frame_number={self.frame_number}, timestamp={self.timestamp_seconds}s)>"
