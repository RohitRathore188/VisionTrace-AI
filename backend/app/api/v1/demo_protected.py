"""
Demo Protected Routes
Examples of role-based access control using authentication dependencies
"""

from fastapi import APIRouter, status

from app.api.dependencies.auth import (
    CurrentActiveUser,
    AdminUser,
    InvestigatorUser,
    ViewerUser,
)
from app.schemas.auth import MessageResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/demo", tags=["Demo - Protected Routes"])


@router.get(
    "/viewer",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Viewer+ access (all authenticated users)",
    description="Accessible by Viewer, Investigator, and Admin roles",
)
async def viewer_route(
    user: ViewerUser,
) -> MessageResponse:
    """
    Route accessible by all authenticated users (Viewer, Investigator, Admin).
    
    Example use case: Viewing videos, search results, reports.
    """
    logger.info("Viewer route accessed", user_id=str(user.id), role=user.role.value)
    
    return MessageResponse(
        message=f"Welcome {user.email}! You have {user.role.value} access.",
        email=user.email
    )


@router.get(
    "/investigator",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Investigator+ access",
    description="Accessible by Investigator and Admin roles only",
)
async def investigator_route(
    user: InvestigatorUser,
) -> MessageResponse:
    """
    Route accessible by Investigators and Admins only.
    
    Example use case: Uploading videos, creating reports, advanced search.
    """
    logger.info("Investigator route accessed", user_id=str(user.id), role=user.role.value)
    
    return MessageResponse(
        message=f"Welcome {user.email}! You have {user.role.value} access. You can upload videos.",
        email=user.email
    )


@router.get(
    "/admin",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Admin only access",
    description="Accessible by Admin role only",
)
async def admin_route(
    admin: AdminUser,
) -> MessageResponse:
    """
    Route accessible by Admins only.
    
    Example use case: User management, system configuration, audit logs.
    """
    logger.info("Admin route accessed", user_id=str(admin.id), role=admin.role.value)
    
    return MessageResponse(
        message=f"Welcome Admin {admin.email}! You have full system access.",
        email=admin.email
    )


@router.get(
    "/profile",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="User profile (any authenticated user)",
    description="Accessible by any authenticated active user",
)
async def profile_route(
    user: CurrentActiveUser,
) -> MessageResponse:
    """
    Route accessible by any authenticated active user.
    
    Example use case: User profile, settings, preferences.
    """
    logger.info("Profile route accessed", user_id=str(user.id), role=user.role.value)
    
    return MessageResponse(
        message=f"Profile for {user.full_name or user.email} ({user.role.value})",
        email=user.email
    )
