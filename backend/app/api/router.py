"""
API Router
Master router that mounts all API versions and endpoints
"""

from fastapi import APIRouter

from app.api.v1 import system, auth, demo_protected, videos, frames, objects, bytetrack, embeddings, search, health
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

# Mount v1 router to main API router
api_router.include_router(v1_router)
