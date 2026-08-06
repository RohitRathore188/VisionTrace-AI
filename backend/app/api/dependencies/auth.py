"""
Authentication Dependencies
FastAPI dependencies for JWT authentication and role-based access control
"""

from typing import Annotated
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.auth_service import auth_service
from app.models.user import User, UserRole
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.core.logging import get_logger

logger = get_logger(__name__)


async def get_token_from_header(
    authorization: Annotated[str | None, Header()] = None
) -> str:
    """
    Extract JWT token from Authorization header.
    
    Args:
        authorization: Authorization header value
    
    Returns:
        JWT token string
    
    Raises:
        UnauthorizedException: If header is missing or invalid
    """
    if not authorization:
        raise UnauthorizedException(
            message="Missing authorization header",
            details={"expected": "Authorization: Bearer <token>"}
        )
    
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException(
            message="Invalid authorization header format",
            details={"expected": "Authorization: Bearer <token>"}
        )
    
    token = authorization.replace("Bearer ", "")
    
    if not token:
        raise UnauthorizedException(
            message="Empty token in authorization header",
            details={"expected": "Authorization: Bearer <token>"}
        )
    
    return token


async def get_current_user(
    token: Annotated[str, Depends(get_token_from_header)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Dependency for protecting routes that require authentication.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
    
    Returns:
        Authenticated User object
    
    Raises:
        UnauthorizedException: If token is invalid or user not found
    
    Usage:
        ```python
        @router.get("/protected")
        async def protected_route(
            current_user: Annotated[User, Depends(get_current_user)]
        ):
            return {"user_id": current_user.id}
        ```
    """
    logger.debug("Authenticating user from token")
    
    user = await auth_service.verify_token(db=db, token=token)
    
    logger.debug("User authenticated", user_id=str(user.id), role=user.role.value)
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current active user (account not deactivated).
    
    Dependency for routes that require an active account.
    
    Args:
        current_user: Authenticated user
    
    Returns:
        Active User object
    
    Raises:
        ForbiddenException: If account is deactivated
    
    Usage:
        ```python
        @router.get("/active-only")
        async def active_route(
            current_user: Annotated[User, Depends(get_current_active_user)]
        ):
            return {"user_id": current_user.id}
        ```
    """
    if not current_user.is_active:
        raise ForbiddenException(
            message="Account is deactivated",
            details={"user_id": str(current_user.id)}
        )
    
    return current_user


async def require_admin(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Require admin role for route access.
    
    Dependency for admin-only routes.
    
    Args:
        current_user: Authenticated active user
    
    Returns:
        Admin User object
    
    Raises:
        ForbiddenException: If user is not an admin
    
    Usage:
        ```python
        @router.delete("/users/{user_id}")
        async def delete_user(
            admin: Annotated[User, Depends(require_admin)],
            user_id: str
        ):
            # Only admins can access this
            return {"deleted": user_id}
        ```
    """
    if current_user.role != UserRole.ADMIN:
        logger.warning(
            "Non-admin user attempted to access admin route",
            user_id=str(current_user.id),
            role=current_user.role.value
        )
        raise ForbiddenException(
            message="Admin access required",
            details={
                "required_role": UserRole.ADMIN.value,
                "user_role": current_user.role.value
            }
        )
    
    logger.debug("Admin access granted", user_id=str(current_user.id))
    
    return current_user


async def require_investigator(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Require investigator or admin role for route access.
    
    Dependency for investigator+ routes (investigator and admin).
    
    Args:
        current_user: Authenticated active user
    
    Returns:
        Investigator or Admin User object
    
    Raises:
        ForbiddenException: If user is not investigator or admin
    
    Usage:
        ```python
        @router.post("/videos")
        async def upload_video(
            investigator: Annotated[User, Depends(require_investigator)],
            file: UploadFile
        ):
            # Investigators and admins can upload videos
            return {"uploaded_by": investigator.id}
        ```
    """
    if current_user.role not in [UserRole.INVESTIGATOR, UserRole.ADMIN]:
        logger.warning(
            "User without investigator access attempted to access investigator route",
            user_id=str(current_user.id),
            role=current_user.role.value
        )
        raise ForbiddenException(
            message="Investigator access required",
            details={
                "required_roles": [UserRole.INVESTIGATOR.value, UserRole.ADMIN.value],
                "user_role": current_user.role.value
            }
        )
    
    logger.debug("Investigator access granted", user_id=str(current_user.id))
    
    return current_user


async def require_viewer(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Require viewer, investigator, or admin role for route access.
    
    Dependency for viewer+ routes (any authenticated active user).
    This is essentially the same as get_current_active_user but more explicit.
    
    Args:
        current_user: Authenticated active user
    
    Returns:
        User object with any role
    
    Usage:
        ```python
        @router.get("/videos")
        async def list_videos(
            viewer: Annotated[User, Depends(require_viewer)]
        ):
            # All authenticated users can view videos
            return {"videos": []}
        ```
    """
    # All active users are at least viewers
    logger.debug("Viewer access granted", user_id=str(current_user.id))
    
    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Create a dependency that requires one of the specified roles.
    
    Factory function for custom role requirements.
    
    Args:
        allowed_roles: One or more UserRole values
    
    Returns:
        FastAPI dependency function
    
    Usage:
        ```python
        @router.post("/reports")
        async def create_report(
            user: Annotated[User, Depends(require_role(UserRole.INVESTIGATOR, UserRole.ADMIN))]
        ):
            # Only investigators and admins can create reports
            return {"report_id": "123"}
        ```
    """
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            logger.warning(
                "User with insufficient role attempted to access protected route",
                user_id=str(current_user.id),
                user_role=current_user.role.value,
                required_roles=[role.value for role in allowed_roles]
            )
            raise ForbiddenException(
                message="Insufficient permissions",
                details={
                    "required_roles": [role.value for role in allowed_roles],
                    "user_role": current_user.role.value
                }
            )
        
        logger.debug(
            "Role check passed",
            user_id=str(current_user.id),
            role=current_user.role.value
        )
        
        return current_user
    
    return role_checker


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(require_admin)]
InvestigatorUser = Annotated[User, Depends(require_investigator)]
ViewerUser = Annotated[User, Depends(require_viewer)]
