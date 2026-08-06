"""
Frame Schemas
Pydantic schemas for frame extraction requests, progress tracking, and keyframe queries
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class FrameExtractionRequest(BaseModel):
    """Request schema to trigger background keyframe extraction"""
    interval_seconds: float = Field(default=1.0, gt=0.0, le=60.0, description="Sampling interval in seconds (e.g. 1 frame every N seconds)")
    jpeg_quality: int = Field(default=85, ge=10, le=100, description="JPEG compression quality (10-100)")


class FrameExtractionProgressResponse(BaseModel):
    """Response schema tracking real-time extraction progress"""
    video_id: UUID
    status: str = Field(..., description="Extraction status: pending, processing, completed, failed")
    total_frames: int = 0
    processed_frames: int = 0
    extracted_count: int = 0
    progress_percent: float = 0.0
    current_timestamp: float = 0.0
    error_message: Optional[str] = None
    retry_count: int = 0
    started_at: Optional[str] = None
    updated_at: Optional[str] = None


class FrameResponse(BaseModel):
    """Response schema for extracted frame metadata"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    video_id: UUID
    frame_number: int
    timestamp_seconds: float
    image_path: str
    width: Optional[int] = None
    height: Optional[int] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    image_url: Optional[str] = Field(None, description="Signed or public URL for keyframe image display")


class FrameListResponse(BaseModel):
    """Paginated list of extracted keyframes for a video"""
    items: List[FrameResponse]
    total: int
    page: int
    page_size: int
    pages: int
