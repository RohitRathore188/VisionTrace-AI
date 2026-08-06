"""
FAISS Search Endpoints (v1)
FastAPI router handling text-to-video and image-to-video visual similarity search, FAISS index sync, and Top-K results ranking.
"""

import time
from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, File, UploadFile, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import get_current_active_user, require_investigator
from app.models.user import User
from app.schemas.search import (
    TextSearchRequest,
    SearchResultItem,
    SearchResponse,
    FAISSBuildIndexResponse,
)
from app.services.faiss_service import faiss_service
from app.services.clip_service import clip_service
from app.core.exceptions import BadRequestException
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/search", tags=["FAISS Vector Search"])


@router.post(
    "/text",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Text-to-Video similarity search",
    description="Encodes natural language query string into 512D OpenCLIP vector, executes FAISS similarity search, and returns Top-K matching keyframes and detected objects with similarity scores."
)
async def search_by_text(
    payload: TextSearchRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Execute text-to-video similarity search"""
    start_t = time.time()
    try:
        stats = faiss_service.get_index_stats()
        if stats["total_vectors"] == 0:
            logger.info("FAISS index is empty. Building index from PostgreSQL database...")
            await faiss_service.build_index_from_db(db)

        # 1. Generate 512D OpenCLIP text query vector
        q_vector = clip_service.generate_text_embedding(payload.query_text)

        # 2. Execute Top-K FAISS similarity search with query_text attribute ranking
        raw_results = faiss_service.search_top_k(
            query_vector=q_vector,
            top_k=payload.top_k,
            video_id=payload.video_id,
            min_score=payload.min_score,
            query_text=payload.query_text
        )

        exec_time = round((time.time() - start_t) * 1000, 2)

        items = []
        for r in raw_results:
            items.append(
                SearchResultItem(
                    type=r.get("type", "frame"),
                    similarity_score=r.get("similarity_score", 0.0),
                    vector_id=r.get("vector_id"),
                    video_id=UUID(r["video_id"]),
                    video_title=r.get("video_title", "Surveillance Video"),
                    frame_id=UUID(r["frame_id"]),
                    object_id=UUID(r["object_id"]) if r.get("object_id") else None,
                    frame_number=r.get("frame_number", 0),
                    timestamp_seconds=r.get("timestamp_seconds", 0.0),
                    image_url=r.get("image_url"),
                    crop_url=r.get("crop_url"),
                    label=r.get("label"),
                    confidence=r.get("confidence"),
                    bounding_box=r.get("bounding_box"),
                )
            )

        logger.info(
            "Executed FAISS text search",
            query=payload.query_text,
            top_k=payload.top_k,
            matches=len(items),
            latency_ms=exec_time,
            user_id=str(current_user.id)
        )

        return SearchResponse(
            query_text=payload.query_text,
            total_matches=len(items),
            execution_time_ms=exec_time,
            results=items
        )
    except Exception as err:
        logger.error(f"Text search failed: {str(err)}", exc_info=True)
        raise BadRequestException(message=f"Search failed: {str(err)}")


@router.post(
    "/image",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Image-to-Video visual similarity search",
    description="Upload query image, generate 512D OpenCLIP visual feature embedding, search FAISS vector index, and return Top-K matches with timestamp, frame, bounding box, and similarity score."
)
async def search_by_image(
    image_file: UploadFile = File(...),
    top_k: int = Form(10),
    video_id: Optional[UUID] = Form(None),
    min_score: float = Form(0.15),
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """Execute Image-to-Video visual similarity search"""
    start_t = time.time()
    try:
        stats = faiss_service.get_index_stats()
        if stats["total_vectors"] == 0:
            logger.info("FAISS index is empty. Building index from PostgreSQL database...")
            await faiss_service.build_index_from_db(db)

        image_bytes = await image_file.read()
        if not image_bytes:
            raise BadRequestException(message="Uploaded image file is empty")

        q_vector = clip_service.generate_image_bytes_embedding(image_bytes)

        raw_results = faiss_service.search_top_k(
            query_vector=q_vector,
            top_k=top_k,
            video_id=video_id,
            min_score=min_score
        )

        exec_time = round((time.time() - start_t) * 1000, 2)

        items = []
        for r in raw_results:
            items.append(
                SearchResultItem(
                    type=r.get("type", "frame"),
                    similarity_score=r.get("similarity_score", 0.0),
                    vector_id=r.get("vector_id"),
                    video_id=UUID(r["video_id"]),
                    video_title=r.get("video_title", "Surveillance Video"),
                    frame_id=UUID(r["frame_id"]),
                    object_id=UUID(r["object_id"]) if r.get("object_id") else None,
                    frame_number=r.get("frame_number", 0),
                    timestamp_seconds=r.get("timestamp_seconds", 0.0),
                    image_url=r.get("image_url"),
                    crop_url=r.get("crop_url"),
                    label=r.get("label"),
                    confidence=r.get("confidence"),
                    bounding_box=r.get("bounding_box"),
                )
            )

        logger.info(
            "Executed FAISS image search",
            filename=image_file.filename,
            top_k=top_k,
            matches=len(items),
            latency_ms=exec_time,
            user_id=str(current_user.id) if current_user else "anonymous"
        )

        return SearchResponse(
            query_text=f"Visual Query: {image_file.filename}",
            total_matches=len(items),
            execution_time_ms=exec_time,
            results=items
        )
    except Exception as err:
        logger.error(f"Image search failed: {str(err)}", exc_info=True)
        raise BadRequestException(message=f"Image search failed: {str(err)}")


@router.post(
    "/build-index",
    response_model=FAISSBuildIndexResponse,
    summary="Build / Sync FAISS index from PostgreSQL embeddings",
    description="Loads 512D OpenCLIP feature vectors from database embeddings table and builds FAISS vector index."
)
async def build_faiss_index(
    current_user: Annotated[User, Depends(require_investigator)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Sync FAISS index from database embeddings"""
    try:
        res = await faiss_service.build_index_from_db(db)
        return FAISSBuildIndexResponse(**res)
    except Exception as err:
        raise BadRequestException(message=f"Failed to build FAISS index: {str(err)}")


@router.get(
    "/index-status",
    summary="Get FAISS index status",
    description="Retrieve total vectors indexed, dimension, and FAISS index configuration."
)
async def get_index_status(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Fetch index status"""
    return faiss_service.get_index_stats()
