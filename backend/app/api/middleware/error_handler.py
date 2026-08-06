"""
Error Handler Middleware
Global exception handler for consistent error responses
"""

from typing import Dict, Any

import structlog
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.exceptions import VisionTraceException

logger = structlog.get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware that catches all exceptions and returns consistent JSON error responses.
    
    Error response format:
    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human-readable error message",
            "details": {...},
            "request_id": "uuid"
        }
    }
    """
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            return await call_next(request)
        except VisionTraceException as e:
            # Handle application exceptions
            return self._create_error_response(
                request=request,
                status_code=e.status_code,
                error_code=e.error_code,
                message=e.message,
                details=e.details,
            )
        except Exception as e:
            # Handle unexpected exceptions
            logger.exception("unhandled_exception", error=str(e))
            return self._create_error_response(
                request=request,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred",
                details={},
            )
    
    def _create_error_response(
        self,
        request: Request,
        status_code: int,
        error_code: str,
        message: str,
        details: Dict[str, Any],
    ) -> JSONResponse:
        """Create a standardized error JSON response"""
        request_id = getattr(request.state, "request_id", None)
        
        error_response = {
            "error": {
                "code": error_code,
                "message": message,
                "request_id": request_id,
            }
        }
        
        # Only include details if non-empty
        if details:
            error_response["error"]["details"] = details
        
        return JSONResponse(
            status_code=status_code,
            content=error_response,
        )
