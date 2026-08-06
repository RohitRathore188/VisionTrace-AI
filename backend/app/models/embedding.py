"""
Embedding Model
SQLAlchemy model for high-dimensional visual & text vector embeddings using pgvector
"""

import uuid
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.db.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.frame import Frame
    from app.models.object import ObjectDetection


# Default embedding vector dimension (CLIP ViT-B/32 standard = 512)
VECTOR_DIMENSION = 512


class Embedding(Base, UUIDMixin, TimestampMixin):
    """
    Embedding model for storing feature vectors of keyframes or cropped objects.
    Enables semantic natural language search and visual similarity search via pgvector.
    """
    
    __tablename__ = "embeddings"
    
    # Foreign key linkage (nullable to allow embedding either whole frames or specific objects)
    frame_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("frames.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Foreign key referencing keyframe ID (if frame-level embedding)"
    )
    
    object_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("objects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Foreign key referencing detected object ID (if object-level embedding)"
    )
    
    # AI Model provenance & configuration
    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="CLIP-ViT-B/32",
        index=True,
        comment="AI model used to generate embedding (e.g., CLIP-ViT-B/32, DINOv2)"
    )
    
    dimension: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=VECTOR_DIMENSION,
        comment="Vector dimension size"
    )
    
    # Vector Embedding storage using pgvector extension
    embedding: Mapped[Vector] = mapped_column(
        Vector(VECTOR_DIMENSION),
        nullable=False,
        comment="512-dimensional vector embedding for ANN similarity search"
    )
    
    # Extensible metadata
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="JSON dictionary for normalization factors or feature extraction metadata"
    )
    
    # Relationships
    frame: Mapped[Optional["Frame"]] = relationship(
        "Frame",
        back_populates="embeddings"
    )
    
    object: Mapped[Optional["ObjectDetection"]] = relationship(
        "ObjectDetection",
        back_populates="embeddings"
    )
    
    def __repr__(self) -> str:
        return f"<Embedding(id={self.id}, model='{self.model_name}', frame_id={self.frame_id}, object_id={self.object_id})>"
