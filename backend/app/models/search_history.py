"""
Search History Model
SQLAlchemy model for logging user search queries, filters, and performance latency
"""

import enum
import uuid
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Text, Float, Integer, Enum as SQLEnum, ForeignKey, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class SearchType(str, enum.Enum):
    """Types of vector & metadata search queries"""
    TEXT = "text"
    IMAGE = "image"
    HYBRID = "hybrid"
    METADATA = "metadata"


class SearchHistory(Base, UUIDMixin, TimestampMixin):
    """
    SearchHistory model logging executed search queries, filter criteria, and response performance metrics.
    """
    
    __tablename__ = "search_history"
    
    # Foreign Key to user
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID who initiated the search query"
    )
    
    # Query Parameters
    query_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Natural language query string (e.g., 'red car in parking lot at night')"
    )
    
    query_image_path: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="Image URL or file path used for visual similarity query"
    )
    
    search_type: Mapped[SearchType] = mapped_column(
        SQLEnum(SearchType, name="searchtype"),
        nullable=False,
        default=SearchType.TEXT,
        index=True,
        comment="Search mechanism type (text, image, hybrid, metadata)"
    )
    
    # Applied Filters JSON (e.g., date range, video IDs, labels, confidence threshold)
    filters: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="JSON dictionary of applied filter parameters"
    )
    
    # Results & Performance Latency Metrics
    result_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of matching video frames or objects returned"
    )
    
    execution_time_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Search execution latency in milliseconds"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="search_histories"
    )
    
    __table_args__ = (
        Index("ix_search_history_user_created", "user_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<SearchHistory(id={self.id}, user_id={self.user_id}, search_type='{self.search_type.value}', result_count={self.result_count})>"
