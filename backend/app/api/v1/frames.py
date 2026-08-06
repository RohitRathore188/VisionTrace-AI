"""
Frame Extraction Endpoints (v1)
FastAPI router handling background keyframe extraction, progress polling, and keyframe queries
"""

import math
from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import get_current_active_user, require_investigator
from app.models.user import User
from app.models.video import Video
from app.models.frame import Frame
from app.schemas.frame import (
    FrameExtractionRequest,
    FrameExtractionProgressResponse,
    FrameResponse,
    FrameListResponse,
)
from app.services.frame_extractor import frame_extraction_service
from app.services.video_service import video_service
from app.services.storage_service import storage_service
from app.core.config import settings
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/videos", tags=["Frame Extraction"])


@router.post(
    "/{video_id}/extract-frames",
    response_model=FrameExtractionProgressResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger background frame extraction",
    description="Enqueues OpenCV frame extraction job for a video with configurable interval sampling."
)
async def trigger_frame_extraction(
    video_id: UUID,
    payload: FrameExtractionRequest,
    current_user: Annotated[User, Depends(require_investigator)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Trigger background keyframe extraction job using OpenCV"""
    video = await video_service.get_video_by_id(db, video_id)
    if not video:
        raise NotFoundException(message="Video not found")
    if video.user_id != current_user.id and not current_user.is_admin:
        raise ForbiddenException(message="Not authorized to process this video")

    try:
        progress_dict = await frame_extraction_service.enqueue_extraction(
            video_id=video_id,
            interval_seconds=payload.interval_seconds,
            jpeg_quality=payload.jpeg_quality
        )
        logger.info(
            "Triggered background frame extraction",
            video_id=str(video_id),
            interval=payload.interval_seconds,
            user_id=str(current_user.id)
        )
        return progress_dict
    except Exception as err:
        raise BadRequestException(message=f"Failed to enqueue extraction: {str(err)}")


@router.get(
    "/{video_id}/extraction/status",
    response_model=FrameExtractionProgressResponse,
    summary="Poll frame extraction progress",
    description="Check real-time status, processed frame count, progress percentage, and timestamps."
)
async def get_extraction_status(
    video_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Fetch extraction progress state"""
    video = await video_service.get_video_by_id(db, video_id)
    if not video:
        raise NotFoundException(message="Video not found")

    progress = frame_extraction_service.get_progress(video_id)
    if not progress:
        # Fallback to database frame count if background job finished
        count_stmt = select(func.count(Frame.id)).where(Frame.video_id == video_id)
        total_extracted = (await db.execute(count_stmt)).scalar_one()

        status_str = "completed" if video.status.value == "completed" else video.status.value
        return {
            "video_id": str(video_id),
            "status": status_str,
            "total_frames": video.total_frames or 0,
            "processed_frames": video.total_frames or 0,
            "extracted_count": total_extracted,
            "progress_percent": 100.0 if total_extracted > 0 else 0.0,
            "current_timestamp": video.duration_seconds or 0.0,
            "error_message": video.error_message,
            "retry_count": 0,
            "started_at": video.updated_at.isoformat(),
            "updated_at": video.updated_at.isoformat(),
        }

    return progress


@router.get(
    "/{video_id}/frames",
    response_model=FrameListResponse,
    summary="List extracted keyframes",
    description="Retrieve paginated keyframes extracted for a specific video."
)
async def list_extracted_frames(
    video_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Frames per page"),
):
    """Fetch paginated keyframes for a video"""
    video = await video_service.get_video_by_id(db, video_id)
    if not video:
        raise NotFoundException(message="Video not found")

    count_stmt = select(func.count(Frame.id)).where(Frame.video_id == video_id)
    total = (await db.execute(count_stmt)).scalar_one()

    offset = (page - 1) * page_size
    query = (
        select(Frame)
        .where(Frame.video_id == video_id)
        .order_by(Frame.frame_number.asc())
        .offset(offset)
        .limit(page_size)
    )

    res = await db.execute(query)
    frames = list(res.scalars().all())

    items = []
    for f in frames:
        image_url = storage_service.get_playback_url(f.image_path, bucket_name=settings.SUPABASE_STORAGE_BUCKET_FRAMES)
        items.append(
            FrameResponse(
                id=f.id,
                video_id=f.video_id,
                frame_number=f.frame_number,
                timestamp_seconds=f.timestamp_seconds,
                image_path=f.image_path,
                width=f.width,
                height=f.height,
                metadata_json=f.metadata_json or {},
                created_at=f.created_at,
                image_url=image_url,
            )
        )

    pages = math.ceil(total / page_size) if total > 0 else 0
    return FrameListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )
