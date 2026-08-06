"""
Custom Exception Classes
Application-specific exceptions with HTTP status code mapping
"""

from typing import Any, Dict, Optional


class VisionTraceException(Exception):
    """Base exception for all VisionTrace-specific errors"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


# Authentication & Authorization Exceptions
class BadRequestException(VisionTraceException):
    """Raised when client sends bad request parameters"""
    def __init__(self, message: str = "Bad request parameters", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, error_code="BAD_REQUEST", details=details)


class UnauthorizedException(VisionTraceException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, error_code="UNAUTHORIZED", details=details)


class ForbiddenException(VisionTraceException):
    """Raised when user lacks required permissions"""
    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, error_code="FORBIDDEN", details=details)


class InvalidCredentialsException(VisionTraceException):
    """Raised when login credentials are invalid"""
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message, status_code=401, error_code="INVALID_CREDENTIALS")


class TokenExpiredException(VisionTraceException):
    """Raised when JWT token has expired"""
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message, status_code=401, error_code="TOKEN_EXPIRED")


class InvalidTokenException(VisionTraceException):
    """Raised when JWT token is invalid"""
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message, status_code=401, error_code="INVALID_TOKEN")


class AccountLockedException(VisionTraceException):
    """Raised when account is locked due to too many failed login attempts"""
    def __init__(self, message: str = "Account locked due to too many failed login attempts"):
        super().__init__(message, status_code=423, error_code="ACCOUNT_LOCKED")


# Resource Exceptions
class NotFoundException(VisionTraceException):
    """Raised when a requested resource is not found"""
    def __init__(self, message: str = "Resource not found", resource: Optional[str] = None, resource_id: Optional[Any] = None):
        if resource and resource_id:
            message = f"{resource} with id '{resource_id}' not found"
        super().__init__(message, status_code=404, error_code="NOT_FOUND", details={"resource": resource, "id": str(resource_id)} if resource else {})


class VideoNotFoundException(NotFoundException):
    """Raised when video is not found"""
    def __init__(self, video_id: str):
        super().__init__(resource="Video", resource_id=video_id)


class UserNotFoundException(NotFoundException):
    """Raised when user is not found"""
    def __init__(self, user_id: str):
        super().__init__(resource="User", resource_id=user_id)


class SessionNotFoundException(NotFoundException):
    """Raised when search session is not found"""
    def __init__(self, session_id: str):
        super().__init__(resource="Search session", resource_id=session_id)


# Conflict Exceptions
class ConflictException(VisionTraceException):
    """Raised when a resource conflict occurs"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=409, error_code="CONFLICT", details=details)


class EmailAlreadyExistsException(ConflictException):
    """Raised when email already exists during registration"""
    def __init__(self, email: str):
        super().__init__(f"Email '{email}' is already registered", details={"email": email})


# Validation Exceptions
class ValidationException(VisionTraceException):
    """Raised when input validation fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR", details=details)


class InvalidFileTypeException(ValidationException):
    """Raised when uploaded file type is not allowed"""
    def __init__(self, filename: str, allowed_types: list[str]):
        super().__init__(
            f"File type not allowed for '{filename}'",
            details={"filename": filename, "allowed_types": allowed_types}
        )


class FileTooLargeException(ValidationException):
    """Raised when uploaded file exceeds size limit"""
    def __init__(self, filename: str, size_mb: float, max_size_mb: int):
        super().__init__(
            f"File '{filename}' ({size_mb:.1f} MB) exceeds maximum size of {max_size_mb} MB",
            details={"filename": filename, "size_mb": size_mb, "max_size_mb": max_size_mb}
        )


class EmptyQueryException(ValidationException):
    """Raised when search query is empty"""
    def __init__(self):
        super().__init__("Search query cannot be empty")


class QueryTooLongException(ValidationException):
    """Raised when text query exceeds maximum length"""
    def __init__(self, length: int, max_length: int = 512):
        super().__init__(
            f"Query length ({length}) exceeds maximum of {max_length} characters",
            details={"length": length, "max_length": max_length}
        )


# Business Logic Exceptions
class UnprocessableException(VisionTraceException):
    """Raised when request is valid but cannot be processed"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, error_code="UNPROCESSABLE", details=details)


class VideoNotReadyException(UnprocessableException):
    """Raised when attempting to search a video that hasn't finished processing"""
    def __init__(self, video_id: str, current_status: str):
        super().__init__(
            f"Video is not ready for search (current status: {current_status})",
            details={"video_id": video_id, "status": current_status}
        )


class NoReadyVideosException(UnprocessableException):
    """Raised when no videos are available for search"""
    def __init__(self):
        super().__init__("No videos are ready for search")


class JobNotInErrorStateException(UnprocessableException):
    """Raised when attempting to retry a job that isn't in error state"""
    def __init__(self, job_id: str, current_state: str):
        super().__init__(
            f"Job cannot be retried (current state: {current_state})",
            details={"job_id": job_id, "current_state": current_state}
        )


# Rate Limiting
class RateLimitExceededException(VisionTraceException):
    """Raised when rate limit is exceeded"""
    def __init__(self, retry_after: int):
        super().__init__(
            "Rate limit exceeded. Please try again later.",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after_seconds": retry_after}
        )


# External Service Exceptions
class ExternalServiceException(VisionTraceException):
    """Raised when external service (Supabase, etc.) fails"""
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"{service} error: {message}",
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, **(details or {})}
        )


class StorageException(ExternalServiceException):
    """Raised when Supabase Storage operation fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("Supabase Storage", message, details)


class DatabaseException(ExternalServiceException):
    """Raised when database operation fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("Database", message, details)
