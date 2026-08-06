"""
Base Pydantic Schemas
Common schema mixins, base classes, error details, and generic response wrappers
"""

from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, List, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {}
        }
    )


class BaseResponse(BaseModel):
    """Generic success response wrapper"""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None


class ErrorDetail(BaseModel):
    """Error detail model"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Generic error response model"""
    success: bool = False
    error: ErrorDetail


class UUIDSchema(BaseSchema):
    """Schema with UUID primary key"""
    id: UUID = Field(..., description="Unique identifier")


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields"""
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class PaginationParams(BaseSchema):
    """Query parameters for pagination"""
    limit: int = Field(default=20, ge=1, le=100, description="Number of items per page")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")


class PaginatedResponse(BaseSchema):
    """Generic paginated response wrapper"""
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Number of items skipped")
    items: list = Field(..., description="List of items")
