"""
ByteTrack Schemas
Pydantic schemas for ByteTrack multi-object tracking runs, trajectory history, and visualization APIs
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field


class ByteTrackRunResponse(BaseModel):
    """Response schema returned after running ByteTrack on video detections"""
    video_id: UUID
    total_frames_processed: int
    objects_tracked: int
    distinct_track_count: int
    status: str = "completed"


class TrackSummaryResponse(BaseModel):
    """Response schema summarizing a distinct object motion track"""
    track_id: int = Field(..., description="Persistent object tracking sequence ID")
    label: str = Field(..., description="Object class label: person, vehicle, bag, phone, laptop, animal")
    total_detections: int
    start_timestamp: float
    end_timestamp: float
    duration_seconds: float
    spatial_displacement: float = Field(..., description="Euclidean displacement of center coordinates across video")
    start_frame_number: int
    end_frame_number: int


class TrajectoryPoint(BaseModel):
    """Single trajectory coordinate along object movement path"""
    object_id: UUID
    frame_id: UUID
    frame_number: int
    timestamp_seconds: float
    center: List[float] = Field(..., description="[center_x, center_y] normalized coordinates")
    bounding_box: Dict[str, float]
    confidence: float
    crop_url: Optional[str] = None
    frame_url: Optional[str] = None


class TrackDetailResponse(BaseModel):
    """Response schema containing full trajectory timeline history for a track_id"""
    video_id: UUID
    track_id: int
    label: str
    total_keyframes: int
    start_timestamp: float
    end_timestamp: float
    trajectory: List[TrajectoryPoint]


class VisualizationPoint(BaseModel):
    """Visualization coordinate point"""
    x: float
    y: float
    timestamp: float
    frame_number: int


class VisualizationTrack(BaseModel):
    """Visualization motion path polyline for overlaying on UI canvas"""
    track_id: int
    label: str
    points: List[VisualizationPoint]
    svg_path: str = Field(..., description="SVG path string (e.g. 'M 0.1,0.2 L 0.15,0.22...')")


class VisualizationResponse(BaseModel):
    """Response schema for trajectory visualization API"""
    video_id: UUID
    tracks: List[VisualizationTrack]
