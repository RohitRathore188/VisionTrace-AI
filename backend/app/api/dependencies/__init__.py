"""
API Dependencies
Reusable FastAPI dependencies for dependency injection
"""

from app.api.dependencies.auth import (
    get_token_from_header,
    get_current_user,
    get_current_active_user,
    require_admin,
    require_investigator,
    require_viewer,
    require_role,
    CurrentUser,
    CurrentActiveUser,
    AdminUser,
    InvestigatorUser,
    ViewerUser,
)

__all__ = [
    "get_token_from_header",
    "get_current_user",
    "get_current_active_user",
    "require_admin",
    "require_investigator",
    "require_viewer",
    "require_role",
    "CurrentUser",
    "CurrentActiveUser",
    "AdminUser",
    "InvestigatorUser",
    "ViewerUser",
]
