"""
Authentication API Endpoints
Handles user registration, login, logout, and password management
"""

from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.auth_service import auth_service
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    ForgotPasswordRequest,
    RefreshTokenRequest,
    AuthResponse,
    MessageResponse,
    UserResponse,
    SessionResponse,
    user_to_response,
)
from app.api.dependencies.auth import get_token_from_header, CurrentActiveUser
from app.models.user import User
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password. Sends verification email.",
)
async def signup(
    request: SignupRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    """
    Register a new user account.
    
    - **email**: User email address (must be unique)
    - **password**: Password (min 8 characters, must contain letter and number)
    - **full_name**: User's full name (optional)
    - **role**: User role - admin, investigator, or viewer (default: viewer)
    
    Returns user information and authentication tokens.
    An email verification link will be sent to the provided email address.
    """
    logger.info("Signup request received", email=request.email, role=request.role.value)
    
    result = await auth_service.signup(
        db=db,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        role=request.role,
    )
    
    logger.info("User signup successful", email=request.email)
    
    return AuthResponse(
        user=UserResponse(**result["user"]),
        session=SessionResponse(**result["session"]),
        message="Account created successfully. Please check your email to verify your account.",
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user with email and password",
)
async def login(
    request: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    """
    Authenticate user with email and password.
    
    - **email**: User email address
    - **password**: User password
    - **remember_me**: Keep user logged in for extended period
    
    Returns user information and authentication tokens.
    """
    logger.info("Login request received", email=request.email, remember_me=request.remember_me)
    
    result = await auth_service.login(
        db=db,
        email=request.email,
        password=request.password,
    )
    
    logger.info("User login successful", email=request.email)
    
    return AuthResponse(
        user=UserResponse(**result["user"]),
        session=SessionResponse(**result["session"]),
        message="Login successful",
    )


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Send password reset email to user",
)
async def forgot_password(
    request: ForgotPasswordRequest,
) -> MessageResponse:
    """
    Request password reset email.
    
    - **email**: User email address
    
    Sends a password reset link to the email if account exists.
    For security, always returns success even if email doesn't exist.
    """
    logger.info("Password reset request received", email=request.email)
    
    result = await auth_service.forgot_password(email=request.email)
    
    logger.info("Password reset email sent", email=request.email)
    
    return MessageResponse(**result)


@router.post(
    "/refresh",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get new access token using refresh token",
)
async def refresh_token(
    request: RefreshTokenRequest,
) -> SessionResponse:
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token from login/signup
    
    Returns new access and refresh tokens.
    """
    logger.info("Token refresh request received")
    
    result = await auth_service.refresh_session(refresh_token=request.refresh_token)
    
    logger.info("Token refresh successful")
    
    return SessionResponse(**result["session"])


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get authenticated user information",
)
async def get_current_user_info(
    current_user: CurrentActiveUser,
) -> UserResponse:
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header (Bearer token).
    
    Returns user profile with role and permissions.
    """
    logger.info("Current user retrieved", user_id=str(current_user.id))
    
    user_dict = user_to_response(current_user)
    
    return UserResponse(**user_dict)


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Sign out user and invalidate session",
)
async def logout(
    token: Annotated[str, Depends(get_token_from_header)],
) -> MessageResponse:
    """
    Logout user and invalidate session.
    
    Requires valid JWT token in Authorization header (Bearer token).
    
    Invalidates the current session in Supabase.
    """
    logger.info("Logout request received")
    
    result = await auth_service.logout(token=token)
    
    logger.info("User logout successful")
    
    return MessageResponse(**result)


@router.get(
    "/health",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Auth service health check",
    description="Check if authentication service is operational",
)
async def health_check() -> MessageResponse:
    """
    Health check endpoint for authentication service.
    
    Returns service status.
    """
    return MessageResponse(message="Authentication service is healthy")
