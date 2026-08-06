"""
ByteTrack Multi-Object Tracking Endpoints (v1)
FastAPI router handling ByteTrack multi-object tracking, persistent track_id assignments, trajectory queries, and visualization APIs.
"""

from typing import Annotated, Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import get_current_active_user, require_investigator
from app.models.user import User
from app.schemas.bytetrack import (
    ByteTrackRunResponse,
    TrackSummaryResponse,
    TrackDetailResponse,
    VisualizationResponse,
)
from app.services.bytetrack_service import bytetrack_service
from app.services.video_service import video_service
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/videos", tags=["ByteTrack Multi-Object Tracking"])


@router.post(
    "/{video_id}/track-objects",
    response_model=ByteTrackRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute ByteTrack multi-object tracking",
    description="Associates detections across sequential frames using ByteTrack Kalman IoU matching and updates persistent track_id values."
)
async def run_bytetrack_tracking(
    video_id: UUID,
    current_user: Annotated[User, Depends(require_investigator)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Execute ByteTrack tracking pipeline"""
    video = await video_service.get_video_by_id(db, video_id)
    if not video:
        raise NotFoundException(message="Video not found")
    if video.user_id != current_user.id and not current_user.is_admin:
        raise ForbiddenException(message="Not authorized to process this video")

    try:
        result = await bytetrack_service.run_bytetrack_for_video(video_id)
        logger.info(
            "Executed ByteTrack tracking",
            video_id=str(video_id),
            distinct_tracks=result["distinct_track_count"],
            user_id=str(current_user.id)
        )
        return result
    except Exception as err:
        raise BadRequestException(message=f"ByteTrack failed: {str(err)}")


@router.get(
    "/{video_id}/tracks",
    response_model=List[TrackSummaryResponse],
    summary="List motion trajectories for video",
    description="Retrieve distinct tracked object motion trajectories with duration, timestamps, and displacement metrics."
)
async def list_video_tracks(
    video_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    min_detections: int = Query(1, ge=1, description="Filter out tracks with fewer than min_detections keyframes")
):
    """List object motion trajectories"""
    video = await video_service.get_video_by_id(db, video_id)
    if not video:
        raise NotFoundException(message="Video not found")

    tracks = await bytetrack_service.get_video_tracks(db, video_id, min_detections=min_detections)
    return tracks


@router.get(
    "/{video_id}/tracks/{track_id}",
    response_model=TrackDetailResponse,
    summary="Get trajectory timeline for a track ID",
    description="Retrieve step-by-step frame coordinates, bounding boxes, and crop URLs for a specific tracked object ID."
)
async def get_track_detail(
    video_id: UUID,
    track_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Fetch trajectory detail for track_id"""
    video = await video_service.get_video_by_id(db, video_id)
    if not video:
        raise NotFoundException(message="Video not found")

    try:
        detail = await bytetrack_service.get_track_detail(db, video_id, track_id)
        return detail
    except ValueError as err:
        raise NotFoundException(message=str(err))


@router.get(
    "/{video_id}/tracks/visualization",
    response_model=VisualizationResponse,
    summary="Get motion trajectory visualization payload",
    description="Provides SVG polyline strings and 2D motion coordinates for rendering motion trajectory lines over video frames."
)
async def get_trajectory_visualization(
    video_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    track_id: Optional[int] = Query(None, description="Optional track ID filter")
):
    """Fetch visualization polyline payload"""
    video = await video_service.get_video_by_id(db, video_id)
    if not video:
        raise NotFoundException(message="Video not found")

    viz_data = await bytetrack_service.get_visualization_payload(db, video_id, track_id=track_id)
    return viz_data
