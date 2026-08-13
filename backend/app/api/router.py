"""
API Router
Master router that mounts all API versions and endpoints
"""

from fastapi import APIRouter

from app.api.v1 import system, auth, demo_protected, videos, frames, objects, bytetrack, embeddings, search, health, dashboard, search_history, admin, cameras, cases, evidence, alerts, audit
from app.core.config import settings

# Create API router
api_router = APIRouter()

# Mount v1 endpoints
v1_router = APIRouter(prefix=settings.API_V1_PREFIX)
v1_router.include_router(system.router)
v1_router.include_router(auth.router)
v1_router.include_router(demo_protected.router)
v1_router.include_router(videos.router)
v1_router.include_router(frames.router)
v1_router.include_router(objects.router)
v1_router.include_router(bytetrack.router)
v1_router.include_router(embeddings.router)
v1_router.include_router(search.router)
v1_router.include_router(health.router)
v1_router.include_router(dashboard.router)
v1_router.include_router(search_history.router)
v1_router.include_router(admin.router)
v1_router.include_router(cameras.router)
v1_router.include_router(cases.router)
v1_router.include_router(evidence.router)
v1_router.include_router(alerts.router)
v1_router.include_router(audit.router)

# Mount v1 router to main API router
api_router.include_router(v1_router)
