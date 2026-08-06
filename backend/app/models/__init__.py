"""
App Models Package
Exports all SQLAlchemy ORM models for database initialization and Alembic migrations
"""

from app.models.role import Role
from app.models.user import User, UserRole
from app.models.video import Video, VideoStatus
from app.models.frame import Frame
from app.models.object import ObjectDetection
from app.models.embedding import Embedding, VECTOR_DIMENSION
from app.models.search_history import SearchHistory, SearchType
from app.models.report import Report, ReportStatus

__all__ = [
    "Role",
    "User",
    "UserRole",
    "Video",
    "VideoStatus",
    "Frame",
    "ObjectDetection",
    "Embedding",
    "VECTOR_DIMENSION",
    "SearchHistory",
    "SearchType",
    "Report",
    "ReportStatus",
]
