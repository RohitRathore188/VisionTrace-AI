"""
OpenCLIP Embeddings Endpoints (v1)
FastAPI router handling OpenCLIP vector embedding generation for frames, detected objects, and text queries.
"""

from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import get_current_active_user, require_investigator
from app.models.user import User
from app.models.embedding import Embedding
from app.schemas.embedding import (
    CLIPEmbeddingRequest,
    TextEmbeddingRequest,
    TextEmbeddingResponse,
    CLIPEmbeddingProgressResponse,
)
from app.services.clip_service import clip_service
from app.services.video_service import video_service
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/embeddings", tags=["OpenCLIP Embeddings"])


@router.post(
    "/text",
    response_model=TextEmbeddingResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate OpenCLIP text query vector",
    description="Encodes natural language search query text into L2-normalized 512-dimensional OpenCLIP vector."
)
async def generate_text_query_embedding(
    payload: TextEmbeddingRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Generate 512D text embedding for search query"""
    try:
        vector = clip_service.generate_text_embedding(payload.query_text)
        return TextEmbeddingResponse(
            query_text=payload.query_text,
            model_name="CLIP-ViT-B-32",
            dimension=512,
            embedding=vector
        )
    except Exception as err:
        raise BadRequestException(message=f"Failed to generate text embedding: {str(err)}")


@router.post(
    "/videos/{video_id}/generate-embeddings",
    response_model=CLIPEmbeddingProgressResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger OpenCLIP visual embedding generation",
    description="Generates 512D OpenCLIP feature vectors for keyframes and cropped objects, persisting to PostgreSQL pgvector."
)
async def trigger_video_embedding_generation(
    video_id: UUID,
    payload: CLIPEmbeddingRequest,
    current_user: Annotated[User, Depends(require_investigator)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Trigger background OpenCLIP embedding job"""
    video = await video_service.get_video_by_id(db, video_id)
    if not video:
        raise NotFoundException(message="Video not found")
    if video.user_id != current_user.id and not current_user.is_admin:
        raise ForbiddenException(message="Not authorized to process this video")

    try:
        progress_dict = await clip_service.enqueue_embedding_generation(
            video_id=video_id,
            include_frames=payload.include_frames,
            include_objects=payload.include_objects
        )
        logger.info(
            "Triggered OpenCLIP embedding generation",
            video_id=str(video_id),
            user_id=str(current_user.id)
        )
        return progress_dict
    except Exception as err:
        raise BadRequestException(message=f"Failed to enqueue embedding job: {str(err)}")


@router.get(
    "/videos/{video_id}/embeddings/status",
    response_model=CLIPEmbeddingProgressResponse,
    summary="Poll OpenCLIP embedding status",
    description="Check real-time status of vector embedding generation."
)
async def get_embedding_status(
    video_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Fetch OpenCLIP embedding status"""
    video = await video_service.get_video_by_id(db, video_id)
    if not video:
        raise NotFoundException(message="Video not found")

    progress = clip_service.get_progress(video_id)
    if not progress:
        # Fallback to database count
        count_f = select(func.count(Embedding.id)).where(Embedding.frame_id.isnot(None))
        count_o = select(func.count(Embedding.id)).where(Embedding.object_id.isnot(None))

        frame_cnt = (await db.execute(count_f)).scalar_one()
        obj_cnt = (await db.execute(count_o)).scalar_one()

        total = frame_cnt + obj_cnt
        return {
            "video_id": str(video_id),
            "status": "completed" if total > 0 else "pending",
            "total_items": total,
            "processed_items": total,
            "frame_embeddings_count": frame_cnt,
            "object_embeddings_count": obj_cnt,
            "progress_percent": 100.0 if total > 0 else 0.0,
            "error_message": video.error_message,
            "started_at": video.updated_at.isoformat(),
            "updated_at": video.updated_at.isoformat(),
        }

    return progress
