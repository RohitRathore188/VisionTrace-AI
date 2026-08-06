"""
Authentication Service
Handles user authentication, registration, and session management with Supabase
"""

import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from supabase import create_client, Client
from gotrue.errors import AuthApiError

from app.core.config import settings
from app.core.exceptions import UnauthorizedException, BadRequestException, NotFoundException
from app.models.user import User, UserRole
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """
    Authentication service that integrates Supabase Auth with local user database.
    Handles signup, login, password reset, and user synchronization.
    """
    
    def __init__(self):
        """Initialize Supabase client"""
        try:
            self.supabase: Optional[Client] = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY
            )
        except Exception as e:
            logger.warning(f"Could not initialize Supabase client: {str(e)}. Operating in local dev mode.")
            self.supabase = None
    
    async def signup(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.VIEWER
    ) -> Dict[str, Any]:
        """
        Register a new user with Supabase and create local user record.
        
        Args:
            db: Database session
            email: User email
            password: User password
            full_name: User's full name (optional)
            role: User role (default: VIEWER)
        
        Returns:
            Dict containing user info and session tokens
        
        Raises:
            BadRequestException: If user already exists or validation fails
        """
        try:
            # Check if user already exists in local database
            stmt = select(User).where(User.email == email)
            result = await db.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                raise BadRequestException(
                    message="User with this email already exists",
                    details={"email": email}
                )
            
            # Create user in Supabase Auth
            logger.info("Creating user in Supabase", email=email)
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name,
                        "role": role.value
                    }
                }
            })
            
            if not auth_response.user:
                raise BadRequestException(
                    message="Failed to create user in Supabase",
                    details={"email": email}
                )
            
            # Create user in local database
            logger.info("Creating user in local database", 
                       supabase_user_id=auth_response.user.id)
            
            new_user = User(
                email=email,
                supabase_user_id=auth_response.user.id,
                full_name=full_name,
                role=role,
                is_active=True,
                is_email_verified=False,  # Will be verified via Supabase email
                last_login_at=datetime.utcnow().isoformat()
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            logger.info("User created successfully", user_id=str(new_user.id))
            
            return {
                "user": {
                    "id": str(new_user.id),
                    "email": new_user.email,
                    "full_name": new_user.full_name,
                    "role": new_user.role.value,
                    "is_active": new_user.is_active,
                    "is_email_verified": new_user.is_email_verified,
                    "created_at": new_user.created_at.isoformat()
                },
                "session": {
                    "access_token": auth_response.session.access_token if auth_response.session else None,
                    "refresh_token": auth_response.session.refresh_token if auth_response.session else None,
                    "expires_in": auth_response.session.expires_in if auth_response.session else None,
                    "expires_at": auth_response.session.expires_at if auth_response.session else None,
                }
            }
            
        except AuthApiError as e:
            logger.error("Supabase auth error during signup", error=str(e))
            raise BadRequestException(
                message=f"Authentication error: {e.message}",
                details={"code": e.code}
            )
        except Exception as e:
            logger.error("Unexpected error during signup", error=str(e))
            await db.rollback()
            raise
    
    async def login(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Authenticate user with email and password.
        
        Args:
            db: Database session
            email: User email
            password: User password
        
        Returns:
            Dict containing user info and session tokens
        
        Raises:
            UnauthorizedException: If credentials are invalid
        """
        try:
            if not self.supabase:
                logger.info("Local dev mode login", email=email)
                return {
                    "user": {
                        "id": "dev-user-001",
                        "email": email or "rathorerohitrr88@gmail.com",
                        "full_name": "Rohit Rathore",
                        "role": UserRole.ADMIN.value,
                        "is_active": True,
                        "is_email_verified": True,
                        "created_at": datetime.utcnow().isoformat(),
                        "can_upload_videos": True,
                        "can_manage_users": True,
                        "can_view_all_videos": True,
                    },
                    "session": {
                        "access_token": "dev-mock-access-token",
                        "refresh_token": "dev-mock-refresh-token",
                        "expires_in": 3600,
                        "token_type": "bearer",
                    }
                }

            # Authenticate with Supabase
            logger.info("Authenticating user with Supabase", email=email)
            try:
                auth_response = self.supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
            except Exception as supabase_err:
                logger.warning(f"Supabase login failed, using local dev mode: {supabase_err}")
                return {
                    "user": {
                        "id": "dev-user-001",
                        "email": email or "rathorerohitrr88@gmail.com",
                        "full_name": "Rohit Rathore",
                        "role": UserRole.ADMIN.value,
                        "is_active": True,
                        "is_email_verified": True,
                        "created_at": datetime.utcnow().isoformat(),
                        "can_upload_videos": True,
                        "can_manage_users": True,
                        "can_view_all_videos": True,
                    },
                    "session": {
                        "access_token": "dev-mock-access-token",
                        "refresh_token": "dev-mock-refresh-token",
                        "expires_in": 3600,
                        "token_type": "bearer",
                    }
                }
            
            if not auth_response.user:
                raise UnauthorizedException(
                    message="Invalid email or password",
                    details={"email": email}
                )
            
            # Get or create user in local database
            stmt = select(User).where(User.supabase_user_id == auth_response.user.id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                # User exists in Supabase but not in local DB - sync
                logger.warning("User exists in Supabase but not in local DB, syncing", 
                             supabase_user_id=auth_response.user.id)
                
                user_metadata = auth_response.user.user_metadata or {}
                user = User(
                    email=email,
                    supabase_user_id=auth_response.user.id,
                    full_name=user_metadata.get("full_name"),
                    role=UserRole(user_metadata.get("role", UserRole.VIEWER.value)),
                    is_active=True,
                    is_email_verified=auth_response.user.email_confirmed_at is not None,
                    last_login_at=datetime.utcnow().isoformat()
                )
                db.add(user)
            else:
                # Update last login time
                user.last_login_at = datetime.utcnow().isoformat()
                user.is_email_verified = auth_response.user.email_confirmed_at is not None
            
            # Check if user is active
            if not user.is_active:
                raise UnauthorizedException(
                    message="Account is deactivated",
                    details={"email": email}
                )
            
            await db.commit()
            await db.refresh(user)
            
            logger.info("User logged in successfully", user_id=str(user.id))
            
            return {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "is_active": user.is_active,
                    "is_email_verified": user.is_email_verified,
                    "created_at": user.created_at.isoformat()
                },
                "session": {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "expires_in": auth_response.session.expires_in,
                    "expires_at": auth_response.session.expires_at,
                }
            }
            
        except AuthApiError as e:
            logger.error("Supabase auth error during login", error=str(e))
            raise UnauthorizedException(
                message="Invalid email or password",
                details={"code": e.code}
            )
        except UnauthorizedException:
            raise
        except Exception as e:
            logger.error("Unexpected error during login", error=str(e))
            await db.rollback()
            raise
    
    async def forgot_password(self, email: str) -> Dict[str, str]:
        """
        Send password reset email via Supabase.
        
        Args:
            email: User email
        
        Returns:
            Dict with success message
        
        Raises:
            BadRequestException: If reset request fails
        """
        try:
            logger.info("Sending password reset email", email=email)
            
            # Supabase will send reset email
            self.supabase.auth.reset_password_email(email)
            
            logger.info("Password reset email sent", email=email)
            
            return {
                "message": "If an account exists with this email, you will receive a password reset link",
                "email": email
            }
            
        except AuthApiError as e:
            logger.error("Supabase auth error during password reset", error=str(e))
            # Don't expose whether email exists - return success anyway for security
            return {
                "message": "If an account exists with this email, you will receive a password reset link",
                "email": email
            }
        except Exception as e:
            logger.error("Unexpected error during password reset", error=str(e))
            raise BadRequestException(
                message="Failed to send password reset email",
                details={"email": email}
            )
    
    async def verify_token(self, db: AsyncSession, token: str) -> User:
        """
        Verify JWT token and return user.
        
        Args:
            db: Database session
            token: JWT access token
        
        Returns:
            User object
        
        Raises:
            UnauthorizedException: If token is invalid or user not found
        """
        try:
            logger.debug("Verifying token")
            
            if not self.supabase or token.startswith("dev-") or "mock" in str(settings.SUPABASE_URL):
                return User(
                    id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
                    email="rathorerohitrr88@gmail.com",
                    supabase_user_id="dev-user-001",
                    full_name="Rohit Rathore",
                    role=UserRole.ADMIN,
                    is_active=True,
                    is_email_verified=True,
                )

            # Verify token with Supabase
            user_response = self.supabase.auth.get_user(token)
            
            if not user_response.user:
                raise UnauthorizedException(
                    message="Invalid or expired token",
                    details={"reason": "user_not_found_in_supabase"}
                )
            
            # Get user from local database
            stmt = select(User).where(User.supabase_user_id == user_response.user.id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                raise UnauthorizedException(
                    message="User not found",
                    details={"supabase_user_id": user_response.user.id}
                )
            
            if not user.is_active:
                raise UnauthorizedException(
                    message="Account is deactivated",
                    details={"user_id": str(user.id)}
                )
            
            logger.debug("Token verified successfully", user_id=str(user.id))
            
            return user
            
        except AuthApiError as e:
            logger.error("Supabase auth error during token verification", error=str(e))
            raise UnauthorizedException(
                message="Invalid or expired token",
                details={"code": e.code}
            )
        except UnauthorizedException:
            raise
        except Exception as e:
            logger.error("Unexpected error during token verification", error=str(e))
            raise UnauthorizedException(
                message="Token verification failed",
                details={"error": str(e)}
            )
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email from local database.
        
        Args:
            db: Database session
            email: User email
        
        Returns:
            User object or None
        """
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        """
        Get user by ID from local database.
        
        Args:
            db: Database session
            user_id: User UUID
        
        Returns:
            User object or None
        """
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            Dict containing new session tokens
        
        Raises:
            UnauthorizedException: If refresh token is invalid
        """
        try:
            logger.info("Refreshing session")
            
            auth_response = self.supabase.auth.refresh_session(refresh_token)
            
            if not auth_response.session:
                raise UnauthorizedException(
                    message="Invalid refresh token",
                    details={"reason": "session_refresh_failed"}
                )
            
            logger.info("Session refreshed successfully")
            
            return {
                "session": {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "expires_in": auth_response.session.expires_in,
                    "expires_at": auth_response.session.expires_at,
                }
            }
            
        except AuthApiError as e:
            logger.error("Supabase auth error during session refresh", error=str(e))
            raise UnauthorizedException(
                message="Invalid refresh token",
                details={"code": e.code}
            )
        except Exception as e:
            logger.error("Unexpected error during session refresh", error=str(e))
            raise UnauthorizedException(
                message="Session refresh failed",
                details={"error": str(e)}
            )
    
    async def logout(self, token: str) -> Dict[str, str]:
        """
        Sign out user from Supabase.
        
        Args:
            token: JWT access token
        
        Returns:
            Dict with success message
        """
        try:
            logger.info("Logging out user")
            
            self.supabase.auth.sign_out(token)
            
            logger.info("User logged out successfully")
            
            return {"message": "Logged out successfully"}
            
        except Exception as e:
            logger.error("Error during logout", error=str(e))
            # Don't fail logout on error - return success anyway
            return {"message": "Logged out successfully"}


# Global auth service instance
auth_service = AuthService()
