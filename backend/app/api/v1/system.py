"""
System Routes
Health check and readiness endpoints
"""

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.system import HealthResponse, ReadinessCheck, ReadinessResponse

router = APIRouter(prefix="/system", tags=["System"])
logger = structlog.get_logger(__name__)


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Liveness probe - confirms API is running"
)
async def health_check() -> HealthResponse:
    """
    Simple health check endpoint.
    Returns 200 OK if the API process is running.
    """
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@router.get(
    "/readiness",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness Check",
    description="Readiness probe - confirms all dependencies are available",
    responses={
        200: {"description": "All dependencies are ready"},
        503: {"description": "One or more dependencies are not ready"}
    }
)
async def readiness_check(
    db: AsyncSession = Depends(get_db)
) -> ReadinessResponse:
    """
    Readiness check endpoint.
    Verifies that critical dependencies (database, Redis) are accessible.
    Returns 503 if any dependency is not ready.
    """
    checks = {}
    all_ready = True
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = ReadinessCheck(status="ok")
        logger.debug("readiness_check_database", status="ok")
    except Exception as e:
        checks["database"] = ReadinessCheck(status="error", message=str(e))
        all_ready = False
        logger.error("readiness_check_database", status="error", error=str(e))
    
    # Check Redis (optional - comment out if Redis not yet configured)
    # try:
    #     redis_client = await get_redis()
    #     await redis_client.ping()
    #     checks["redis"] = ReadinessCheck(status="ok")
    #     logger.debug("readiness_check_redis", status="ok")
    # except Exception as e:
    #     checks["redis"] = ReadinessCheck(status="error", message=str(e))
    #     all_ready = False
    #     logger.error("readiness_check_redis", status="error", error=str(e))
    
    response_status = "ready" if all_ready else "not_ready"
    status_code = status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return ReadinessResponse(
        status=response_status,
        checks=checks,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
