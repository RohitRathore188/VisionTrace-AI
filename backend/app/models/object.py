"""
Object Model
SQLAlchemy model for AI-detected objects, bounding box annotations, and tracking
"""

import uuid
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Float, Integer, ForeignKey, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.video import Video
    from app.models.frame import Frame
    from app.models.embedding import Embedding


class ObjectDetection(Base, UUIDMixin, TimestampMixin):
    """
    ObjectDetection model representing objects detected within video keyframes (e.g. YOLO, Faster R-CNN).
    """
    
    __tablename__ = "objects"
    
    # Foreign Keys
    frame_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("frames.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key referencing keyframe ID"
    )
    
    video_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Denormalized foreign key referencing video ID for direct query optimization"
    )
    
    # Tracking ID across frames (e.g., DeepSORT / ByteTrack ID)
    track_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        comment="Multi-object tracking sequence ID across sequential frames"
    )
    
    # Object Class Label & Confidence Score
    label: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Object class label (e.g., person, car, bag, bicycle)"
    )
    
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
        comment="Detection confidence score between 0.0 and 1.0"
    )
    
    # Bounding Box Coordinates: {"xmin": 0.1, "ymin": 0.2, "xmax": 0.4, "ymax": 0.8}
    bounding_box: Mapped[Dict[str, float]] = mapped_column(
        JSON,
        nullable=False,
        comment="Normalized bounding box coordinates {xmin, ymin, xmax, ymax}"
    )
    
    # Cropped object thumbnail reference
    crop_path: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="File path or URL storing cropped image of detected object"
    )
    
    # Additional AI detection metadata (e.g., color, pose, attribute classifications)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="JSON dictionary for additional attributes (color, direction, pose)"
    )
    
    # Relationships
    frame: Mapped["Frame"] = relationship(
        "Frame",
        back_populates="objects"
    )
    
    video: Mapped["Video"] = relationship(
        "Video",
        back_populates="objects"
    )
    
    embeddings: Mapped[List["Embedding"]] = relationship(
        "Embedding",
        back_populates="object",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("ix_objects_label_confidence", "label", "confidence"),
        Index("ix_objects_video_track", "video_id", "track_id"),
    )
    
    def __repr__(self) -> str:
        return f"<ObjectDetection(id={self.id}, label='{self.label}', confidence={self.confidence:.2f}, track_id={self.track_id})>"
