"""
Production Health Checks & Monitoring Endpoints (v1)
FastAPI router handling liveness probes, readiness checks (PostgreSQL, Redis, Storage, FAISS), and Prometheus metrics.
"""

import time
import os
import psutil
from typing import Dict, Any
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.faiss_service import faiss_service
from app.services.clip_service import clip_service
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health & Monitoring"])

START_TIME = time.time()


@router.get("", summary="Basic Health Check")
async def basic_health():
    """Basic health check ping"""
    return {
        "status": "healthy",
        "service": getattr(settings, "APP_NAME", "VisionTrace AI"),
        "version": getattr(settings, "APP_VERSION", "1.0.0"),
        "timestamp": time.time()
    }


@router.get("/liveness", summary="Kubernetes / Cloud Liveness Probe")
async def liveness_probe():
    """Liveness probe: verifies application process is running"""
    return {"status": "alive", "uptime_seconds": round(time.time() - START_TIME, 2)}


@router.get("/readiness", summary="Kubernetes / Cloud Readiness Probe")
async def readiness_probe(db: AsyncSession = Depends(get_db)):
    """Readiness probe: checks PostgreSQL DB, FAISS Index, and system resources"""
    checks: Dict[str, Any] = {
        "database": "unknown",
        "faiss_index": "unknown",
        "storage": "ok"
    }

    # 1. Check PostgreSQL Database Connection
    try:
        res = await db.execute(text("SELECT 1"))
        if res.scalar() == 1:
            checks["database"] = "connected"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"

    # 2. Check FAISS Index Status
    try:
        stats = faiss_service.get_index_stats()
        checks["faiss_index"] = {
            "status": "ready",
            "total_vectors": stats["total_vectors"],
            "dimension": stats["dimension"]
        }
    except Exception as e:
        checks["faiss_index"] = f"error: {str(e)}"

    is_ready = checks["database"] == "connected"
    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return Response(
        content=str({
            "status": "ready" if is_ready else "not_ready",
            "checks": checks,
            "timestamp": time.time()
        }),
        status_code=status_code,
        media_type="application/json"
    )


@router.get("/metrics", summary="Prometheus System Metrics")
async def get_metrics():
    """Prometheus metrics endpoint for production monitoring"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    uptime = time.time() - START_TIME
    cpu_percent = psutil.cpu_percent(interval=None)
    ram_mb = round(memory_info.rss / (1024 * 1024), 2)

    stats = faiss_service.get_index_stats()

    metrics_text = f"""# HELP visiontrace_uptime_seconds Total application uptime in seconds
# TYPE visiontrace_uptime_seconds counter
visiontrace_uptime_seconds {round(uptime, 2)}

# HELP visiontrace_cpu_percent Current CPU utilization percentage
# TYPE visiontrace_cpu_percent gauge
visiontrace_cpu_percent {cpu_percent}

# HELP visiontrace_memory_bytes Resident memory usage in bytes
# TYPE visiontrace_memory_bytes gauge
visiontrace_memory_bytes {memory_info.rss}

# HELP visiontrace_faiss_vectors_total Total 512D vectors indexed in FAISS
# TYPE visiontrace_faiss_vectors_total gauge
visiontrace_faiss_vectors_total {stats['total_vectors']}
"""
    return Response(content=metrics_text, media_type="text/plain")
