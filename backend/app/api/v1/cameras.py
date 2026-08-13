"""
Camera API Endpoints (v1)
FastAPI router for surveillance camera management, IP camera health status, and channel configuration
"""

import uuid
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.api.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.camera import Camera, CameraStatus

router = APIRouter(prefix="/cameras", tags=["Camera Management"])


class CameraResponse(BaseModel):
    id: uuid.UUID
    name: str
    location: str
    zone: str
    rtsp_url: Optional[str] = None
    status: str
    resolution: str
    fps: float

    class Config:
        from_attributes = True


class CameraCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    location: str = Field(default="Main Building")
    zone: str = Field(default="Perimeter")
    rtsp_url: Optional[str] = None
    status: CameraStatus = Field(default=CameraStatus.ONLINE)
    resolution: str = Field(default="1920x1080")
    fps: float = Field(default=30.0)


@router.get("", response_model=List[CameraResponse])
async def list_cameras(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """List all registered surveillance cameras and health telemetry"""
    stmt = select(Camera).where(Camera.is_deleted == False).order_by(Camera.name)
    res = await db.execute(stmt)
    cameras = list(res.scalars().all())

    # Seed default cameras if table is empty
    if not cameras:
        default_cams = [
            Camera(name="CAM-01 (Main Gate)", location="North Perimeter", zone="Entrance", status=CameraStatus.ONLINE, resolution="1920x1080", fps=30.0),
            Camera(name="CAM-02 (Parking Lot B)", location="West Field", zone="Parking", status=CameraStatus.ONLINE, resolution="1920x1080", fps=30.0),
            Camera(name="CAM-03 (Loading Dock)", location="East Facility", zone="Restricted", status=CameraStatus.ONLINE, resolution="3840x2160", fps=60.0),
            Camera(name="CAM-04 (Server Room Lobby)", location="HQ Floor 2", zone="High Security", status=CameraStatus.DEGRADED, resolution="1920x1080", fps=24.0),
            Camera(name="CAM-05 (South Perimeter)", location="South Wall", zone="Fence", status=CameraStatus.OFFLINE, resolution="1920x1080", fps=30.0),
        ]
        db.add_all(default_cams)
        await db.commit()
        res = await db.execute(stmt)
        cameras = list(res.scalars().all())

    return cameras


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    payload: CameraCreateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """Register a new surveillance camera channel"""
    cam = Camera(
        id=uuid.uuid4(),
        name=payload.name,
        location=payload.location,
        zone=payload.zone,
        rtsp_url=payload.rtsp_url,
        status=payload.status,
        resolution=payload.resolution,
        fps=payload.fps
    )
    db.add(cam)
    await db.commit()
    await db.refresh(cam)
    return cam
