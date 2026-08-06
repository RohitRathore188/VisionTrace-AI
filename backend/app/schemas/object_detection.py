"""
Object Detection Schemas
Pydantic schemas for YOLO object detection requests, progress tracking, and detected object query responses
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class BoundingBoxSchema(BaseModel):
    """Normalized bounding box coordinates (0.0 to 1.0)"""
    xmin: float = Field(..., ge=0.0, le=1.0)
    ymin: float = Field(..., ge=0.0, le=1.0)
    xmax: float = Field(..., ge=0.0, le=1.0)
    ymax: float = Field(..., ge=0.0, le=1.0)


class YOLODetectionRequest(BaseModel):
    """Request schema to trigger YOLO object detection pipeline"""
    confidence_threshold: float = Field(default=0.25, ge=0.05, le=1.0, description="Minimum detection confidence threshold")
    target_classes: Optional[List[str]] = Field(
        default=None,
        description="Optional list of target classes (person, vehicle, bag, phone, laptop, animal)"
    )


class YOLODetectionProgressResponse(BaseModel):
    """Response schema tracking object detection status"""
    video_id: UUID
    status: str = Field(..., description="Detection status: pending, processing, completed, failed")
    total_frames: int = 0
    processed_frames: int = 0
    detected_objects_count: int = 0
    progress_percent: float = 0.0
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    updated_at: Optional[str] = None


class ObjectResponse(BaseModel):
    """Response schema for a detected object entity"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    frame_id: UUID
    video_id: UUID
    track_id: Optional[int] = None
    label: str = Field(..., description="Detected class label: person, vehicle, bag, phone, laptop, animal")
    confidence: float
    bounding_box: BoundingBoxSchema
    crop_path: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    timestamp_seconds: Optional[float] = Field(None, description="Frame timestamp in seconds")
    frame_number: Optional[int] = Field(None, description="Frame sequence number")
    crop_url: Optional[str] = Field(None, description="Playback URL for cropped object image")


class ObjectListResponse(BaseModel):
    """Paginated list of detected object entities"""
    items: List[ObjectResponse]
    total: int
    page: int
    page_size: int
    pages: int
