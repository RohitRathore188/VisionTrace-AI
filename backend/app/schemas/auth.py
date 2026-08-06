"""
Authentication Schemas
Pydantic models for authentication requests and responses
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.user import UserRole


# Request Schemas

class SignupRequest(BaseModel):
    """User registration request"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 characters)"
    )
    full_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="User's full name"
    )
    role: Optional[UserRole] = Field(
        default=UserRole.VIEWER,
        description="User role (default: viewer)"
    )
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        has_letter = any(c.isalpha() for c in v)
        has_number = any(c.isdigit() for c in v)
        
        if not (has_letter and has_number):
            raise ValueError("Password must contain at least one letter and one number")
        
        return v
    
    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate full name"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v


# Alias for RegisterRequest
RegisterRequest = SignupRequest


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(
        default=False,
        description="Remember login session"
    )


class ForgotPasswordRequest(BaseModel):
    """Password reset request"""
    email: EmailStr = Field(..., description="User email address")


class ResetPasswordRequest(BaseModel):
    """Password reset with token"""
    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password (min 8 characters)"
    )
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        has_letter = any(c.isalpha() for c in v)
        has_number = any(c.isdigit() for c in v)
        
        if not (has_letter and has_number):
            raise ValueError("Password must contain at least one letter and one number")
        
        return v


class RefreshTokenRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str = Field(..., description="Refresh token")


# Response Schemas

class SessionResponse(BaseModel):
    """Authentication session tokens"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    expires_at: Optional[int] = Field(None, description="Access token expiration timestamp")
    token_type: str = Field(default="bearer", description="Token type")


class UserResponse(BaseModel):
    """User information response"""
    id: str = Field(..., description="User UUID")
    email: str = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User's full name")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Account active status")
    is_email_verified: bool = Field(..., description="Email verification status")
    created_at: str = Field(..., description="Account creation timestamp")
    last_login_at: Optional[str] = Field(None, description="Last login timestamp")
    
    can_upload_videos: bool = Field(..., description="Can upload videos")
    can_manage_users: bool = Field(..., description="Can manage users")
    can_view_all_videos: bool = Field(..., description="Can view all videos")
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Complete authentication response with user and session"""
    user: UserResponse
    session: SessionResponse
    message: Optional[str] = Field(None, description="Optional message")


# Aliases for response schemas
LoginResponse = AuthResponse
RefreshTokenResponse = SessionResponse


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str = Field(..., description="Response message")
    email: Optional[str] = Field(None, description="Email address (if applicable)")


class TokenVerificationResponse(BaseModel):
    """Token verification response"""
    valid: bool = Field(..., description="Token validity")
    user: Optional[UserResponse] = Field(None, description="User info if valid")


def user_to_response(user) -> dict:
    """Convert User model to UserResponse dict"""
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
        "is_active": user.is_active,
        "is_email_verified": user.is_email_verified,
        "created_at": user.created_at.isoformat() if hasattr(user.created_at, 'isoformat') else str(user.created_at),
        "last_login_at": user.last_login_at.isoformat() if hasattr(user, 'last_login_at') and user.last_login_at and hasattr(user.last_login_at, 'isoformat') else None,
        "can_upload_videos": user.can_upload_videos,
        "can_manage_users": user.can_manage_users,
        "can_view_all_videos": user.can_view_all_videos,
    }
