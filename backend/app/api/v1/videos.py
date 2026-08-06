"""
Video Endpoints (v1)
FastAPI router handling video upload initialization, chunked uploads, status tracking, and metadata management
"""

import math
from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, File, UploadFile, Form, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import get_current_active_user, require_investigator
from app.models.user import User
from app.models.video import VideoStatus
from app.schemas.video import (
    VideoUploadInitRequest,
    VideoUploadInitResponse,
    VideoChunkUploadResponse,
    VideoUploadCompleteRequest,
    VideoResponse,
    VideoStatusResponse,
    VideoListResponse,
)
from app.services.video_service import video_service
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/videos", tags=["Videos"])


@router.post(
    "/upload/init",
    response_model=VideoUploadInitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initialize video upload session",
    description="Validates file parameters, creates a pending video database record, and generates Supabase upload tokens."
)
async def init_video_upload(
    payload: VideoUploadInitRequest,
    current_user: Annotated[User, Depends(require_investigator)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Initialize video upload session and create pending record"""
    try:
        _, response = await video_service.init_upload(
            db=db,
            user_id=current_user.id,
            payload=payload
        )
        logger.info(
            "Initialized video upload",
            video_id=str(response.video_id),
            user_id=str(current_user.id),
            filename=payload.filename
        )
        return response
    except ValueError as err:
        raise BadRequestException(message=str(err))


@router.post(
    "/upload/chunk",
    response_model=VideoChunkUploadResponse,
    summary="Upload video chunk (Resumable upload fallback)",
    description="Accepts chunked binary data for large video file uploads with pause/resume support."
)
async def upload_video_chunk(
    video_id: UUID = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    chunk_file: UploadFile = File(...),
    current_user: Annotated[User, Depends(require_investigator)] = None,
    db: AsyncSession = Depends(get_db),
):
    """Upload video binary chunk"""
    chunk_bytes = await chunk_file.read()
    try:
        res = await video_service.handle_chunk_upload(
            db=db,
            video_id=video_id,
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            chunk_bytes=chunk_bytes
        )
        return res
    except ValueError as err:
        raise BadRequestException(message=str(err))


@router.post(
    "/{video_id}/complete",
    response_model=VideoResponse,
    summary="Complete video upload session",
    description="Finalizes upload, persists extracted technical metadata, and marks status as completed."
)
async def complete_video_upload(
    video_id: UUID,
    payload: VideoUploadCompleteRequest,
    current_user: Annotated[User, Depends(require_investigator)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Finalize video upload and save technical metadata"""
    video = await video_service.get_video_by_id(db, video_id)
    if not video:
        raise NotFoundException(message="Video not found")
    if video.user_id != current_user.id and not current_user.is_admin:
        raise ForbiddenException(message="Not authorized to modify this video")

    try:
        updated_video = await video_service.complete_upload(
            db=db,
            video_id=video_id,
            payload=payload
        )
        logger.info(
            "Completed video upload",
            video_id=str(video_id),
            user_id=str(current_user.id),
            status=updated_video.status.value
        )
        return video_service.format_video_response(updated_video)
    except ValueError as err:
        raise BadRequestException(message=str(err))


@router.get(
    "",
    response_model=VideoListResponse,
    summary="List uploaded videos",
    description="Retrieve paginated list of uploaded videos for current user."
)
async def list_videos(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[VideoStatus] = Query(None, alias="status", description="Filter by status")
):
    """List videos with pagination and status filter"""
    videos, total = await video_service.list_videos(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status_filter
    )

    items = [video_service.format_video_response(v) for v in videos]
    pages = math.ceil(total / page_size) if total > 0 else 0

    return VideoListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get(
    "/{video_id}",
    response_model=VideoResponse,
    summary="Get video details",
    description="Retrieve details and playback URL for a specific video."
)
async def get_video(
    video_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Fetch video metadata by UUID"""
    video = await video_service.get_video_by_id(db, video_id)
    if not video:
        raise NotFoundException(message="Video not found")
    if video.user_id != current_user.id and not current_user.is_admin:
        raise ForbiddenException(message="Not authorized to access this video")

    return video_service.format_video_response(video)


@router.get(
    "/{video_id}/status",
    response_model=VideoStatusResponse,
    summary="Track video status",
    description="Poll current ingestion and processing status for a video."
)
async def get_video_status(
    video_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Track video status"""
    video = await video_service.get_video_by_id(db, video_id)
    if not video:
        raise NotFoundException(message="Video not found")
    if video.user_id != current_user.id and not current_user.is_admin:
        raise ForbiddenException(message="Not authorized to access this video")

    progress = 100.0 if video.status == VideoStatus.COMPLETED else (50.0 if video.status == VideoStatus.PROCESSING else 0.0)

    return VideoStatusResponse(
        video_id=video.id,
        status=video.status,
        progress_percent=progress,
        error_message=video.error_message,
        updated_at=video.updated_at
    )


@router.delete(
    "/{video_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete video",
    description="Soft delete video record and remove asset from storage."
)
async def delete_video(
    video_id: UUID,
    current_user: Annotated[User, Depends(require_investigator)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete video asset"""
    success = await video_service.delete_video(db, video_id, current_user.id)
    if not success:
        raise NotFoundException(message="Video not found or access denied")
    return None
