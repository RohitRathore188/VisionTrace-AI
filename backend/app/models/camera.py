"""
Camera Model
SQLAlchemy model for surveillance camera nodes, IP streams, and operational health status
"""

import enum
import uuid
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlalchemy import String, Text, Float, Integer, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user import User


class CameraStatus(str, enum.Enum):
    """Operational health status of camera node"""
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class Camera(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Surveillance Camera Model representing hardware IP cameras, CCTV feeds, or virtual channels.
    """
    __tablename__ = "cameras"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Human-readable camera name (e.g., CAM-01 North Gate)"
    )

    location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Main Building",
        comment="Physical location or facility zone"
    )

    zone: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Perimeter",
        comment="Security zone (e.g., Perimeter, RestrictArea, ServerRoom, Parking)"
    )

    rtsp_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="RTSP stream URL for live IP monitoring"
    )

    status: Mapped[CameraStatus] = mapped_column(
        SQLEnum(CameraStatus, name="camerastatus"),
        nullable=False,
        default=CameraStatus.ONLINE,
        index=True,
        comment="Operational state (online, degraded, offline, maintenance)"
    )

    resolution: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="1920x1080",
        comment="Video stream resolution"
    )

    fps: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=30.0,
        comment="Recording framerate"
    )

    metadata_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Extensible telemetry metadata"
    )

    def __repr__(self) -> str:
        return f"<Camera(id={self.id}, name='{self.name}', status='{self.status.value}')>"
