"""
Schemas Package
Exports all Pydantic schemas for request/response serialization
"""

from app.schemas.base import BaseResponse, ErrorDetail, ErrorResponse, PaginatedResponse
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    UserResponse,
)
from app.schemas.system import HealthCheckResponse
from app.schemas.video import (
    VideoBase,
    VideoUploadInitRequest,
    VideoUploadInitResponse,
    VideoChunkUploadResponse,
    VideoUploadCompleteRequest,
    VideoResponse,
    VideoStatusResponse,
    VideoListResponse,
)
from app.schemas.frame import (
    FrameExtractionRequest,
    FrameExtractionProgressResponse,
    FrameResponse,
    FrameListResponse,
)
from app.schemas.object_detection import (
    BoundingBoxSchema,
    YOLODetectionRequest,
    YOLODetectionProgressResponse,
    ObjectResponse,
    ObjectListResponse,
)
from app.schemas.bytetrack import (
    ByteTrackRunResponse,
    TrackSummaryResponse,
    TrajectoryPoint,
    TrackDetailResponse,
    VisualizationPoint,
    VisualizationTrack,
    VisualizationResponse,
)
from app.schemas.embedding import (
    CLIPEmbeddingRequest,
    TextEmbeddingRequest,
    TextEmbeddingResponse,
    CLIPEmbeddingProgressResponse,
)
from app.schemas.search import (
    TextSearchRequest,
    SearchResultItem,
    SearchResponse,
    FAISSBuildIndexResponse,
)

__all__ = [
    "BaseResponse",
    "ErrorDetail",
    "ErrorResponse",
    "PaginatedResponse",
    "LoginRequest",
    "LoginResponse",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    "RegisterRequest",
    "UserResponse",
    "HealthCheckResponse",
    "VideoBase",
    "VideoUploadInitRequest",
    "VideoUploadInitResponse",
    "VideoChunkUploadResponse",
    "VideoUploadCompleteRequest",
    "VideoResponse",
    "VideoStatusResponse",
    "VideoListResponse",
    "FrameExtractionRequest",
    "FrameExtractionProgressResponse",
    "FrameResponse",
    "FrameListResponse",
    "BoundingBoxSchema",
    "YOLODetectionRequest",
    "YOLODetectionProgressResponse",
    "ObjectResponse",
    "ObjectListResponse",
    "ByteTrackRunResponse",
    "TrackSummaryResponse",
    "TrajectoryPoint",
    "TrackDetailResponse",
    "VisualizationPoint",
    "VisualizationTrack",
    "VisualizationResponse",
    "CLIPEmbeddingRequest",
    "TextEmbeddingRequest",
    "TextEmbeddingResponse",
    "CLIPEmbeddingProgressResponse",
    "TextSearchRequest",
    "SearchResultItem",
    "SearchResponse",
    "FAISSBuildIndexResponse",
]
