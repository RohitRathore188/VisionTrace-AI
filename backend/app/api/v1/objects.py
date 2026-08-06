"""
Object Detection Endpoints (v1)
FastAPI router handling YOLO object detection pipeline triggering, status polling, and detected object query API
"""

import math
from typing import Annotated, Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.session import get_db
from app.api.dependencies.auth import get_current_active_user, require_investigator
from app.models.user import User
from app.models.video import Video
from app.models.frame import Frame
from app.models.object import ObjectDetection
from app.schemas.object_detection import (
    YOLODetectionRequest,
    YOLODetectionProgressResponse,
    ObjectResponse,
    ObjectListResponse,
    BoundingBoxSchema,
)
from app.services.yolo_service import yolo_service
from app.services.video_service import video_service
from app.services.storage_service import storage_service
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/videos", tags=["Object Detection"])


@router.post(
    "/{video_id}/detect-objects",
    response_model=YOLODetectionProgressResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger YOLO object detection pipeline",
    description="Runs YOLO object detection on extracted video keyframes. Detects person, vehicle, bag, phone, laptop, animal."
)
async def trigger_object_detection(
    video_id: UUID,
    payload: YOLODetectionRequest,
    current_user: Annotated[User, Depends(require_investigator)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Trigger background YOLO detection job"""
    video = await video_service.get_video_by_id(db, video_id)
    if not video:
        raise NotFoundException(message="Video not found")
    if video.user_id != current_user.id and not current_user.is_admin:
        raise ForbiddenException(message="Not authorized to process this video")

    # Check keyframe count
    count_stmt = select(func.count(Frame.id)).where(Frame.video_id == video_id)
    frame_count = (await db.execute(count_stmt)).scalar_one()
    if frame_count == 0:
        raise BadRequestException(message="No extracted keyframes found. Please run keyframe extraction first.")

    try:
        progress_dict = await yolo_service.enqueue_detection(
            video_id=video_id,
            confidence_threshold=payload.confidence_threshold,
            target_classes=payload.target_classes
        )
        logger.info(
            "Triggered YOLO object detection",
            video_id=str(video_id),
            conf=payload.confidence_threshold,
            user_id=str(current_user.id)
        )
        return progress_dict
    except Exception as err:
        raise BadRequestException(message=f"Failed to enqueue object detection: {str(err)}")


@router.get(
    "/{video_id}/objects/status",
    response_model=YOLODetectionProgressResponse,
    summary="Poll object detection progress",
    description="Check real-time status of YOLO object detection background task."
)
async def get_object_detection_status(
    video_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Fetch object detection status"""
    video = await video_service.get_video_by_id(db, video_id)
    if not video:
        raise NotFoundException(message="Video not found")

    progress = yolo_service.get_progress(video_id)
    if not progress:
        count_stmt = select(func.count(ObjectDetection.id)).where(ObjectDetection.video_id == video_id)
        total_objects = (await db.execute(count_stmt)).scalar_one()

        return {
            "video_id": str(video_id),
            "status": "completed" if total_objects > 0 else "pending",
            "total_frames": video.total_frames or 0,
            "processed_frames": video.total_frames or 0,
            "detected_objects_count": total_objects,
            "progress_percent": 100.0 if total_objects > 0 else 0.0,
            "error_message": video.error_message,
            "started_at": video.updated_at.isoformat(),
            "updated_at": video.updated_at.isoformat(),
        }

    return progress


@router.get(
    "/{video_id}/objects",
    response_model=ObjectListResponse,
    summary="List detected objects for video",
    description="Retrieve paginated list of detected objects (person, vehicle, bag, phone, laptop, animal) with bounding box annotations."
)
async def list_video_objects(
    video_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    label: Optional[str] = Query(None, description="Filter by class label: person, vehicle, bag, phone, laptop, animal"),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="Minimum confidence score threshold")
):
    """List detected objects for a video with filtering"""
    video = await video_service.get_video_by_id(db, video_id)
    if not video:
        raise NotFoundException(message="Video not found")

    count_query = select(func.count(ObjectDetection.id)).where(ObjectDetection.video_id == video_id)
    query = (
        select(ObjectDetection)
        .options(joinedload(ObjectDetection.frame))
        .where(ObjectDetection.video_id == video_id)
    )

    if label:
        count_query = count_query.where(ObjectDetection.label == label.lower())
        query = query.where(ObjectDetection.label == label.lower())
    if min_confidence > 0.0:
        count_query = count_query.where(ObjectDetection.confidence >= min_confidence)
        query = query.where(ObjectDetection.confidence >= min_confidence)

    total = (await db.execute(count_query)).scalar_one()

    offset = (page - 1) * page_size
    query = query.order_by(desc(ObjectDetection.confidence)).offset(offset).limit(page_size)

    res = await db.execute(query)
    objects = list(res.scalars().all())

    items = []
    for obj in objects:
        bbox = BoundingBoxSchema(**obj.bounding_box)
        crop_url = storage_service.get_playback_url(obj.crop_path) if obj.crop_path else None
        items.append(
            ObjectResponse(
                id=obj.id,
                frame_id=obj.frame_id,
                video_id=obj.video_id,
                track_id=obj.track_id,
                label=obj.label,
                confidence=obj.confidence,
                bounding_box=bbox,
                crop_path=obj.crop_path,
                metadata_json=obj.metadata_json or {},
                created_at=obj.created_at,
                timestamp_seconds=obj.frame.timestamp_seconds if obj.frame else None,
                frame_number=obj.frame.frame_number if obj.frame else None,
                crop_url=crop_url,
            )
        )

    pages = math.ceil(total / page_size) if total > 0 else 0
    return ObjectListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get(
    "/frames/{frame_id}/objects",
    response_model=List[ObjectResponse],
    summary="Get detected objects for a keyframe",
    description="Retrieve all bounding box annotations and class labels detected in a single keyframe."
)
async def list_frame_objects(
    frame_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Fetch objects for a specific frame"""
    stmt = (
        select(ObjectDetection)
        .options(joinedload(ObjectDetection.frame))
        .where(ObjectDetection.frame_id == frame_id)
        .order_by(desc(ObjectDetection.confidence))
    )
    res = await db.execute(stmt)
    objects = list(res.scalars().all())

    items = []
    for obj in objects:
        bbox = BoundingBoxSchema(**obj.bounding_box)
        crop_url = storage_service.get_playback_url(obj.crop_path) if obj.crop_path else None
        items.append(
            ObjectResponse(
                id=obj.id,
                frame_id=obj.frame_id,
                video_id=obj.video_id,
                track_id=obj.track_id,
                label=obj.label,
                confidence=obj.confidence,
                bounding_box=bbox,
                crop_path=obj.crop_path,
                metadata_json=obj.metadata_json or {},
                created_at=obj.created_at,
                timestamp_seconds=obj.frame.timestamp_seconds if obj.frame else None,
                frame_number=obj.frame.frame_number if obj.frame else None,
                crop_url=crop_url,
            )
        )

    return items
