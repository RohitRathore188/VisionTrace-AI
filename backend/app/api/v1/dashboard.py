"""
Dashboard Stats Endpoint (v1)
Returns aggregated real-time system metrics: video counts by status,
search activity, FAISS index stats, and recent search history.
"""

import time
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.video import Video, VideoStatus
from app.models.search_history import SearchHistory
from app.services.faiss_service import faiss_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/stats",
    summary="Get dashboard statistics",
    description="Returns aggregated real-time stats: video counts by status, search history counts, FAISS index info, and recent activity."
)
async def get_dashboard_stats(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Aggregate dashboard stats for the authenticated user (admins see global stats)."""
    start_t = time.time()

    # ── Video Counts ──────────────────────────────────────────────
    # Admins see all videos; other roles see only their own
    video_q = (
        select(Video.status, func.count(Video.id).label("count"))
        .where(Video.deleted_at.is_(None))
        .group_by(Video.status)
    )
    if not current_user.is_admin:
        video_q = video_q.where(Video.user_id == current_user.id)

    video_stats_q = await db.execute(video_q)
    video_rows = video_stats_q.all()

    video_counts = {
        "total": 0,
        "pending": 0,
        "processing": 0,
        "completed": 0,
        "failed": 0,
    }
    for row in video_rows:
        status_key = row.status.value if hasattr(row.status, "value") else str(row.status)
        video_counts[status_key] = row.count
        video_counts["total"] += row.count

    # ── Search History Counts ─────────────────────────────────────
    if current_user.is_admin:
        search_count_q = await db.execute(
            select(func.count(SearchHistory.id))
        )
    else:
        search_count_q = await db.execute(
            select(func.count(SearchHistory.id))
            .where(SearchHistory.user_id == current_user.id)
        )
    total_searches = search_count_q.scalar() or 0

    # Recent 5 searches
    if current_user.is_admin:
        recent_q = await db.execute(
            select(SearchHistory)
            .order_by(SearchHistory.created_at.desc())
            .limit(5)
        )
    else:
        recent_q = await db.execute(
            select(SearchHistory)
            .where(SearchHistory.user_id == current_user.id)
            .order_by(SearchHistory.created_at.desc())
            .limit(5)
        )
    recent_searches = recent_q.scalars().all()

    recent_activity = []
    for s in recent_searches:
        recent_activity.append({
            "id": str(s.id),
            "query_text": s.query_text,
            "search_type": s.search_type.value,
            "result_count": s.result_count,
            "execution_time_ms": s.execution_time_ms,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })

    # ── FAISS Index Stats ─────────────────────────────────────────
    try:
        faiss_stats = faiss_service.get_index_stats()
    except Exception:
        faiss_stats = {"total_vectors": 0, "dimension": 512}

    exec_time = round((time.time() - start_t) * 1000, 2)

    logger.info(
        "Dashboard stats fetched",
        user_id=str(current_user.id),
        total_videos=video_counts["total"],
        total_searches=total_searches,
        latency_ms=exec_time,
    )

    return {
        "videos": video_counts,
        "searches": {
            "total": total_searches,
        },
        "faiss_index": {
            "total_vectors": faiss_stats.get("total_vectors", 0),
            "dimension": faiss_stats.get("dimension", 512),
        },
        "recent_activity": recent_activity,
        "execution_time_ms": exec_time,
    }
