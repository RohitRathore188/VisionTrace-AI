"""
Search History Endpoints (v1)
FastAPI router for listing, retrieving, and deleting user search history records.
"""

from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.search_history import SearchHistory
from app.core.exceptions import NotFoundException, ForbiddenException
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/search-history", tags=["Search History"])


@router.get(
    "",
    summary="List search history",
    description="Returns paginated search history for the current user, ordered by most recent first."
)
async def list_search_history(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List paginated search history for the current user."""
    offset = (page - 1) * page_size

    # Admins see all; others see only their own
    if current_user.is_admin:
        count_q = await db.execute(select(func.count(SearchHistory.id)))
        items_q = await db.execute(
            select(SearchHistory)
            .order_by(SearchHistory.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
    else:
        count_q = await db.execute(
            select(func.count(SearchHistory.id))
            .where(SearchHistory.user_id == current_user.id)
        )
        items_q = await db.execute(
            select(SearchHistory)
            .where(SearchHistory.user_id == current_user.id)
            .order_by(SearchHistory.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )

    total = count_q.scalar() or 0
    items = items_q.scalars().all()

    serialized = []
    for s in items:
        serialized.append({
            "id": str(s.id),
            "query_text": s.query_text,
            "query_image_path": s.query_image_path,
            "search_type": s.search_type.value,
            "filters": s.filters,
            "result_count": s.result_count,
            "execution_time_ms": s.execution_time_ms,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "user_id": str(s.user_id),
        })

    return {
        "items": serialized,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": max(1, (total + page_size - 1) // page_size),
    }


@router.get(
    "/{history_id}",
    summary="Get single search history entry",
    description="Retrieve details of a specific search history record."
)
async def get_search_history_entry(
    history_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single search history entry."""
    result = await db.execute(
        select(SearchHistory).where(SearchHistory.id == history_id)
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise NotFoundException(message="Search history entry not found")

    if entry.user_id != current_user.id and not current_user.is_admin:
        raise ForbiddenException(message="Not authorized to access this record")

    return {
        "id": str(entry.id),
        "query_text": entry.query_text,
        "query_image_path": entry.query_image_path,
        "search_type": entry.search_type.value,
        "filters": entry.filters,
        "result_count": entry.result_count,
        "execution_time_ms": entry.execution_time_ms,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "user_id": str(entry.user_id),
    }


@router.delete(
    "/clear",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear all search history",
    description="Delete all search history entries for the current user."
)
async def clear_search_history(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Clear all search history for the current user."""
    await db.execute(
        delete(SearchHistory).where(SearchHistory.user_id == current_user.id)
    )
    await db.commit()
    logger.info("Cleared search history", user_id=str(current_user.id))
    return None


@router.delete(
    "/{history_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete search history entry",
    description="Delete a single search history record by ID."
)
async def delete_search_history_entry(
    history_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a single search history entry."""
    result = await db.execute(
        select(SearchHistory).where(SearchHistory.id == history_id)
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise NotFoundException(message="Search history entry not found")

    if entry.user_id != current_user.id and not current_user.is_admin:
        raise ForbiddenException(message="Not authorized to delete this record")

    await db.delete(entry)
    await db.commit()
    logger.info("Deleted search history entry", entry_id=str(history_id), user_id=str(current_user.id))
    return None
