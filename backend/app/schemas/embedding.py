"""
OpenCLIP Embedding Schemas
Pydantic schemas for vector embedding generation requests, progress polling, and text query embeddings
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field


class CLIPEmbeddingRequest(BaseModel):
    """Request schema to trigger OpenCLIP feature vector embedding generation"""
    include_frames: bool = Field(default=True, description="Generate 512D visual embeddings for whole keyframes")
    include_objects: bool = Field(default=True, description="Generate 512D visual embeddings for cropped detected objects")


class TextEmbeddingRequest(BaseModel):
    """Request schema to generate OpenCLIP text query vector"""
    query_text: str = Field(..., min_length=1, max_length=500, description="Natural language search query text")


class TextEmbeddingResponse(BaseModel):
    """Response schema containing normalized 512D OpenCLIP text embedding vector"""
    query_text: str
    model_name: str = "CLIP-ViT-B-32"
    dimension: int = 512
    embedding: List[float] = Field(..., description="512-dimensional normalized float vector")


class CLIPEmbeddingProgressResponse(BaseModel):
    """Response schema tracking embedding generation status"""
    video_id: UUID
    status: str = Field(..., description="Embedding status: pending, processing, completed, failed")
    total_items: int = 0
    processed_items: int = 0
    frame_embeddings_count: int = 0
    object_embeddings_count: int = 0
    progress_percent: float = 0.0
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    updated_at: Optional[str] = None
