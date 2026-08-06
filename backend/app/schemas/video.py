"""
Video Schemas
Pydantic schemas for video upload, status tracking, and metadata management
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.models.video import VideoStatus


class VideoBase(BaseModel):
    """Base video schema with common attributes"""
    title: str = Field(..., min_length=1, max_length=255, description="Video title or camera identifier")
    description: Optional[str] = Field(None, description="Optional video description")
    metadata_json: Dict[str, Any] = Field(default_factory=dict, description="Custom camera or ingestion metadata")


class VideoUploadInitRequest(VideoBase):
    """Request schema for initializing a video upload session"""
    filename: str = Field(..., description="Original video filename")
    file_size_bytes: int = Field(..., gt=0, description="Total file size in bytes")
    mime_type: str = Field(default="video/mp4", description="Video MIME type")
    duration_seconds: Optional[float] = Field(None, ge=0.0, description="Video duration in seconds")
    fps: Optional[float] = Field(None, ge=0.0, description="Video frames per second")
    width: Optional[int] = Field(None, ge=0, description="Video width in pixels")
    height: Optional[int] = Field(None, ge=0, description="Video height in pixels")


class VideoUploadInitResponse(BaseModel):
    """Response schema returned after initializing a video upload"""
    video_id: UUID = Field(..., description="Created video UUID")
    upload_url: Optional[str] = Field(None, description="Supabase presigned upload URL or backend upload endpoint")
    storage_path: str = Field(..., description="Target bucket storage path")
    bucket_name: str = Field(..., description="Supabase storage bucket name")
    chunk_size: int = Field(default=5 * 1024 * 1024, description="Recommended chunk size for upload (5MB)")
    resumable: bool = Field(default=True, description="Whether resumable upload is enabled")


class VideoChunkUploadResponse(BaseModel):
    """Response schema after uploading a video chunk"""
    video_id: UUID
    chunk_index: int
    total_chunks: int
    bytes_received: int
    total_bytes_received: int
    is_complete: bool


class VideoUploadCompleteRequest(BaseModel):
    """Request schema to finalize a video upload session"""
    file_path: str = Field(..., description="Storage path in bucket or local storage")
    file_size_bytes: int = Field(..., gt=0, description="Final file size in bytes")
    mime_type: Optional[str] = Field("video/mp4", description="MIME type")
    duration_seconds: Optional[float] = Field(None, ge=0.0, description="Video duration in seconds")
    fps: Optional[float] = Field(None, ge=0.0, description="Video frames per second")
    width: Optional[int] = Field(None, ge=0, description="Video width in pixels")
    height: Optional[int] = Field(None, ge=0, description="Video height in pixels")
    total_frames: Optional[int] = Field(None, ge=0, description="Total frame count")
    metadata_json: Optional[Dict[str, Any]] = Field(default_factory=dict)


class VideoResponse(VideoBase):
    """Response schema for video objects"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    file_path: str
    file_size_bytes: Optional[int] = None
    mime_type: str
    duration_seconds: Optional[float] = None
    fps: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    total_frames: Optional[int] = None
    status: VideoStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    playback_url: Optional[str] = Field(None, description="Signed or public URL for video preview/playback")


class VideoStatusResponse(BaseModel):
    """Response schema for tracking video status"""
    video_id: UUID
    status: VideoStatus
    progress_percent: float = Field(default=100.0, description="Upload / ingestion progress percentage")
    error_message: Optional[str] = None
    updated_at: datetime


class VideoListResponse(BaseModel):
    """Paginated response for video listing"""
    items: List[VideoResponse]
    total: int
    page: int
    page_size: int
    pages: int
