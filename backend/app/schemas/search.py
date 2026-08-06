"""
FAISS Search Schemas
Pydantic schemas for text-to-video visual similarity search and top-K results
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field


class TextSearchRequest(BaseModel):
    """Request schema for text-to-video visual similarity search"""
    query_text: str = Field(..., min_length=1, max_length=500, description="Natural language search query string")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of top closest matching results to return")
    video_id: Optional[UUID] = Field(default=None, description="Optional video ID filter")
    min_score: float = Field(default=0.15, ge=0.0, le=1.0, description="Minimum similarity score threshold")


class SearchResultItem(BaseModel):
    """Individual Top-K search result item with similarity score"""
    type: str = Field(..., description="Matched entity type: 'frame' or 'object'")
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    vector_id: Optional[int] = None
    video_id: UUID
    video_title: Optional[str] = "Surveillance Video"
    frame_id: UUID
    object_id: Optional[UUID] = None
    frame_number: int
    timestamp_seconds: float
    image_url: Optional[str] = Field(None, description="Keyframe image playback URL")
    crop_url: Optional[str] = Field(None, description="Cropped object image URL")
    label: Optional[str] = Field(None, description="Object class label if object match")
    confidence: Optional[float] = Field(None, description="Detection confidence score")
    bounding_box: Optional[Dict[str, float]] = Field(None, description="Bounding box coordinates")


class SearchResponse(BaseModel):
    """Response schema for vector similarity search"""
    query_text: str
    total_matches: int
    execution_time_ms: float
    results: List[SearchResultItem]


class FAISSBuildIndexResponse(BaseModel):
    """Response schema for build/sync index API"""
    status: str
    total_indexed: int
    dimension: int
    index_type: str
