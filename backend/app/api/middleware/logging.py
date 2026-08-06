"""
Logging Middleware
Logs HTTP requests and responses with structured context
"""

import time

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all HTTP requests and responses.
    Includes:
    - Request method, path, and client IP
    - Response status code and duration
    - Request ID from RequestIDMiddleware
    """
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Start timer
        start_time = time.time()
        
        # Extract request details
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else None
        client_ip = request.client.host if request.client else None
        
        # Bind context for this request
        structlog.contextvars.bind_contextvars(
            method=method,
            path=path,
            client_ip=client_ip,
        )
        
        # Log request
        logger.info(
            "request_started",
            query_params=query_params,
        )
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Log response
            log_level = "error" if status_code >= 500 else "warning" if status_code >= 400 else "info"
            getattr(logger, log_level)(
                "request_completed",
                status_code=status_code,
                duration_ms=duration_ms,
            )
            
            return response
            
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(
                "request_failed",
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=duration_ms,
            )
            raise
