"""
Admin Endpoints (v1)
FastAPI router for admin-only system metrics, user management, and pipeline job oversight.
All routes require the Admin role.
"""

import time
from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, Body
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import require_admin
from app.models.user import User, UserRole
from app.models.video import Video, VideoStatus
from app.models.search_history import SearchHistory
from app.services.faiss_service import faiss_service
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ──────────────────────────────────────────────────────────────────
# System Metrics
# ──────────────────────────────────────────────────────────────────

@router.get(
    "/metrics",
    summary="Get system-wide metrics",
    description="Returns aggregate system metrics: user counts, video counts by status, total searches, FAISS vectors, and system uptime."
)
async def get_admin_metrics(
    admin: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return system-wide aggregated metrics for admin dashboard."""
    start_t = time.time()

    # Total users by role
    user_role_q = await db.execute(
        select(User.role, func.count(User.id).label("count"))
        .where(User.deleted_at.is_(None))
        .group_by(User.role)
    )
    user_role_rows = user_role_q.all()

    user_counts = {"total": 0, "admin": 0, "investigator": 0, "viewer": 0, "active": 0, "inactive": 0}
    for row in user_role_rows:
        role_key = row.role.value if hasattr(row.role, "value") else str(row.role)
        user_counts[role_key] = row.count
        user_counts["total"] += row.count

    active_q = await db.execute(
        select(func.count(User.id)).where(User.is_active.is_(True)).where(User.deleted_at.is_(None))
    )
    user_counts["active"] = active_q.scalar() or 0
    user_counts["inactive"] = user_counts["total"] - user_counts["active"]

    # Video counts by status
    video_status_q = await db.execute(
        select(Video.status, func.count(Video.id).label("count"))
        .where(Video.deleted_at.is_(None))
        .group_by(Video.status)
    )
    video_rows = video_status_q.all()

    video_counts = {"total": 0, "pending": 0, "processing": 0, "completed": 0, "failed": 0}
    for row in video_rows:
        status_key = row.status.value if hasattr(row.status, "value") else str(row.status)
        video_counts[status_key] = row.count
        video_counts["total"] += row.count

    # Total searches
    total_search_q = await db.execute(select(func.count(SearchHistory.id)))
    total_searches = total_search_q.scalar() or 0

    # FAISS stats
    try:
        faiss_stats = faiss_service.get_index_stats()
    except Exception:
        faiss_stats = {"total_vectors": 0, "dimension": 512}

    exec_time = round((time.time() - start_t) * 1000, 2)

    return {
        "users": user_counts,
        "videos": video_counts,
        "searches": {"total": total_searches},
        "faiss_index": {
            "total_vectors": faiss_stats.get("total_vectors", 0),
            "dimension": faiss_stats.get("dimension", 512),
        },
        "execution_time_ms": exec_time,
    }


# ──────────────────────────────────────────────────────────────────
# User Management
# ──────────────────────────────────────────────────────────────────

@router.get(
    "/users",
    summary="List all users",
    description="Paginated list of all registered users with role and account status."
)
async def list_users(
    admin: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role_filter: Optional[str] = Query(None, alias="role"),
    active_only: bool = Query(False),
):
    """Return paginated list of all users for admin management."""
    offset = (page - 1) * page_size

    base_q = select(User).where(User.deleted_at.is_(None))
    count_base_q = select(func.count(User.id)).where(User.deleted_at.is_(None))

    if role_filter:
        try:
            role_enum = UserRole(role_filter)
            base_q = base_q.where(User.role == role_enum)
            count_base_q = count_base_q.where(User.role == role_enum)
        except ValueError:
            raise BadRequestException(message=f"Invalid role: {role_filter}")

    if active_only:
        base_q = base_q.where(User.is_active.is_(True))
        count_base_q = count_base_q.where(User.is_active.is_(True))

    count_result = await db.execute(count_base_q)
    total = count_result.scalar() or 0

    users_result = await db.execute(
        base_q.order_by(User.created_at.desc()).offset(offset).limit(page_size)
    )
    users = users_result.scalars().all()

    serialized = []
    for u in users:
        serialized.append({
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value,
            "is_active": u.is_active,
            "is_email_verified": u.is_email_verified,
            "last_login_at": u.last_login_at,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })

    return {
        "items": serialized,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": max(1, (total + page_size - 1) // page_size),
    }


@router.put(
    "/users/{user_id}",
    summary="Update user role or status",
    description="Admin can update a user's role (admin/investigator/viewer) or toggle active status."
)
async def update_user(
    user_id: UUID,
    admin: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
    role: Optional[str] = Body(None, embed=True),
    is_active: Optional[bool] = Body(None, embed=True),
):
    """Update a user's role or active status."""
    result = await db.execute(
        select(User).where(User.id == user_id).where(User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException(message="User not found")

    if role is not None:
        try:
            user.role = UserRole(role)
        except ValueError:
            raise BadRequestException(message=f"Invalid role: {role}. Must be one of: admin, investigator, viewer")

    if is_active is not None:
        user.is_active = is_active

    await db.commit()
    await db.refresh(user)

    logger.info(
        "Admin updated user",
        target_user_id=str(user_id),
        admin_id=str(admin.id),
        new_role=role,
        new_active=is_active,
    )

    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "is_active": user.is_active,
        "is_email_verified": user.is_email_verified,
        "last_login_at": user.last_login_at,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


# ──────────────────────────────────────────────────────────────────
# Pipeline Jobs (Video Processing Status)
# ──────────────────────────────────────────────────────────────────

@router.get(
    "/jobs",
    summary="List pipeline jobs",
    description="Returns recent video processing jobs with their current status."
)
async def list_pipeline_jobs(
    admin: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """List all video processing jobs for pipeline monitoring."""
    offset = (page - 1) * page_size

    base_q = select(Video).where(Video.deleted_at.is_(None))
    count_q = select(func.count(Video.id)).where(Video.deleted_at.is_(None))

    if status_filter:
        try:
            status_enum = VideoStatus(status_filter)
            base_q = base_q.where(Video.status == status_enum)
            count_q = count_q.where(Video.status == status_enum)
        except ValueError:
            raise BadRequestException(message=f"Invalid status: {status_filter}")

    total_result = await db.execute(count_q)
    total = total_result.scalar() or 0

    videos_result = await db.execute(
        base_q.order_by(Video.updated_at.desc()).offset(offset).limit(page_size)
    )
    videos = videos_result.scalars().all()

    serialized = []
    for v in videos:
        serialized.append({
            "video_id": str(v.id),
            "title": v.title,
            "status": v.status.value,
            "user_id": str(v.user_id),
            "file_size_bytes": v.file_size_bytes,
            "duration_seconds": v.duration_seconds,
            "error_message": v.error_message,
            "created_at": v.created_at.isoformat() if v.created_at else None,
            "updated_at": v.updated_at.isoformat() if v.updated_at else None,
        })

    return {
        "items": serialized,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": max(1, (total + page_size - 1) // page_size),
    }
