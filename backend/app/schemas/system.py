"""
System Schemas
Health check and system status schemas
"""

from typing import Dict, Optional
from pydantic import Field
from app.schemas.base import BaseSchema


class HealthResponse(BaseSchema):
    """Health check response"""
    status: str = Field(..., description="Health status", examples=["ok"])
    timestamp: str = Field(..., description="Current timestamp")


# Alias for HealthCheckResponse
HealthCheckResponse = HealthResponse


class ReadinessCheck(BaseSchema):
    """Individual service readiness check"""
    status: str = Field(..., description="Service status", examples=["ok", "error"])
    message: Optional[str] = Field(None, description="Error message if status is error")


class ReadinessResponse(BaseSchema):
    """Readiness check response"""
    status: str = Field(..., description="Overall readiness status", examples=["ready", "not_ready"])
    checks: Dict[str, ReadinessCheck] = Field(..., description="Individual service checks")
    timestamp: str = Field(..., description="Current timestamp")
