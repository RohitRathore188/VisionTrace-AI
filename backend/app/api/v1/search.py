"""
FAISS Search Endpoints (v1)
FastAPI router handling text-to-video and image-to-video visual similarity search, FAISS index sync, and Top-K results ranking.
"""

import time
from typing import Annotated, Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, File, UploadFile, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import get_current_active_user, require_investigator
from app.models.user import User
from app.models.search_history import SearchHistory, SearchType
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


async def _save_search_history(
    db: AsyncSession,
    user_id,
    search_type: SearchType,
    query_text: Optional[str],
    query_image_path: Optional[str],
    result_count: int,
    execution_time_ms: float,
    filters: dict = None,
) -> None:
    """Persist a search history record and audit log entry to the database."""
    try:
        from app.models.audit import AuditLog
        record = SearchHistory(
            user_id=user_id,
            search_type=search_type,
            query_text=query_text,
            query_image_path=query_image_path,
            result_count=result_count,
            execution_time_ms=execution_time_ms,
            filters=filters or {},
        )
        db.add(record)

        audit = AuditLog(
            user_id=user_id,
            user_email=getattr(user_id, "email", "operator@visiontrace.ai"),
            action="FAISS_VECTOR_SEARCH",
            resource_type="search",
            resource_id=search_type.value if hasattr(search_type, "value") else str(search_type),
            result_status="SUCCESS",
            details_json={
                "query": query_text or query_image_path or "visual_search",
                "result_count": result_count,
                "execution_time_ms": execution_time_ms
            }
        )
        db.add(audit)
        await db.commit()
    except Exception as e:
        logger.warning("Failed to persist search history or audit log", error=str(e))


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
    """Execute text-to-video similarity search with full debug logging"""
    import time as _time
    start_t = _time.time()

    # -- [1] Log received query ------------------------------------------------
    recv_msg = (
        f"\n{'#'*70}\n"
        f"[SEARCH REQUEST] Received query_text : '{payload.query_text}'\n"
        f"[SEARCH REQUEST] top_k              : {payload.top_k}\n"
        f"[SEARCH REQUEST] min_score          : {payload.min_score}\n"
        f"[SEARCH REQUEST] video_id filter    : {payload.video_id}\n"
        f"{'#'*70}"
    )
    logger.info(recv_msg)
    print(recv_msg, flush=True)

    try:
        # -- Auto-build FAISS index if empty ----------------------------------
        stats = faiss_service.get_index_stats()
        if stats["total_vectors"] == 0 or len(faiss_service._metadata_map) == 0:
            logger.info("[SEARCH] FAISS index is empty. Building index from database...")
            print("[SEARCH] FAISS index is empty - building index now...", flush=True)
            await faiss_service.build_index_from_db(db)

        stats_after = faiss_service.get_index_stats()
        index_size_msg = (
            f"[SEARCH] FAISS index size at search time: {stats_after['total_vectors']} vectors"
        )
        logger.info(index_size_msg)
        print(index_size_msg, flush=True)

        # -- [4] Generate a FRESH OpenCLIP text embedding for every request ----
        # No caching - always freshly computed from the model.
        q_vector = clip_service.generate_text_embedding(payload.query_text)

        # -- [5][6] Print first 10 values and verify embedding changes ---------
        import numpy as np
        q_arr = np.array(q_vector, dtype=np.float32)
        q_norm = float(np.linalg.norm(q_arr))
        embedding_msg = (
            f"[EMBEDDING GENERATED]\n"
            f"  Query         : '{payload.query_text}'\n"
            f"  Dimension     : {len(q_vector)}\n"
            f"  L2 Norm       : {q_norm:.6f}\n"
            f"  Preview [0:10]: {[round(v, 6) for v in q_vector[:10]]}\n"
            f"  Preview[10:20]: {[round(v, 6) for v in q_vector[10:20]]}"
        )
        logger.info(embedding_msg)
        print(embedding_msg, flush=True)

        if q_norm < 0.01:
            logger.error("[EMBEDDING ERROR] Generated embedding is near-zero - CLIP model likely failed!")
            print("[EMBEDDING ERROR] Near-zero embedding! Check CLIP model.", flush=True)

        # -- [7][8][9][10] FAISS search - search_top_k logs distances/IDs ------
        raw_results = faiss_service.search_top_k(
            query_vector=q_vector,
            top_k=payload.top_k,
            video_id=payload.video_id,
            video_ids=payload.video_ids,
            min_score=payload.min_score,
            query_text=payload.query_text
        )

        exec_time = round((_time.time() - start_t) * 1000, 2)

        items = []
        for r in raw_results:
            try:
                items.append(
                    SearchResultItem(
                        type=r.get("type", "frame"),
                        similarity_score=r.get("similarity_score", 0.0),
                        vector_id=r.get("vector_id"),
                        video_id=UUID(r["video_id"]),
                        video_title=r.get("video_title", "Surveillance Video"),
                        camera_name=r.get("camera_name", "CAM-01 (Main Gate)"),
                        frame_id=UUID(r["frame_id"]),
                        object_id=UUID(r["object_id"]) if r.get("object_id") else None,
                        frame_number=r.get("frame_number", 0),
                        timestamp_seconds=r.get("timestamp_seconds", 0.0),
                        video_playback_url=r.get("video_playback_url"),
                        image_url=r.get("image_url"),
                        crop_url=r.get("crop_url"),
                        label=r.get("label"),
                        confidence=r.get("confidence"),
                        bounding_box=r.get("bounding_box"),
                    )
                )
            except Exception as item_err:
                logger.warning(f"[RESULT PARSE ERROR] Skipping result: {item_err} | raw: {r}")

        summary_msg = (
            f"[SEARCH COMPLETE] Query: '{payload.query_text}' | "
            f"Results: {len(items)} | Latency: {exec_time}ms"
        )
        logger.info(summary_msg)
        print(summary_msg, flush=True)

        # Persist search to history
        await _save_search_history(
            db=db,
            user_id=current_user.id,
            search_type=SearchType.TEXT,
            query_text=payload.query_text,
            query_image_path=None,
            result_count=len(items),
            execution_time_ms=exec_time,
            filters={"top_k": payload.top_k, "min_score": payload.min_score},
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
    video_ids: Optional[List[UUID]] = Form(None),
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
            video_ids=video_ids,
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
                    camera_name=r.get("camera_name", "CAM-01 (Main Gate)"),
                    frame_id=UUID(r["frame_id"]),
                    object_id=UUID(r["object_id"]) if r.get("object_id") else None,
                    frame_number=r.get("frame_number", 0),
                    timestamp_seconds=r.get("timestamp_seconds", 0.0),
                    video_playback_url=r.get("video_playback_url"),
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

        # Persist search to history
        if current_user:
            await _save_search_history(
                db=db,
                user_id=current_user.id,
                search_type=SearchType.IMAGE,
                query_text=f"Visual Query: {image_file.filename}",
                query_image_path=image_file.filename,
                result_count=len(items),
                execution_time_ms=exec_time,
                filters={"top_k": top_k, "min_score": min_score},
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
