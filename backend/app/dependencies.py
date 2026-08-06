"""
FastAPI Dependencies
Shared dependencies for dependency injection
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    
    Yields:
        AsyncSession: Database session that auto-commits on success and rolls back on error
        
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Placeholder for future auth dependencies
# async def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: AsyncSession = Depends(get_db)
# ) -> User:
#     """Get current authenticated user from JWT token"""
#     ...

# async def require_role(required_role: UserRole):
#     """Dependency factory that requires specific user role"""
#     async def role_checker(current_user: User = Depends(get_current_user)):
#         if current_user.role != required_role:
#             raise ForbiddenException()
#         return current_user
#     return role_checker
