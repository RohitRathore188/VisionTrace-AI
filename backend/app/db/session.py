"""
Database Session Management
Async SQLAlchemy session factory and engine configuration
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from sqlalchemy import text
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

db_url_str = str(settings.DATABASE_URL)
engine_kwargs = {"echo": settings.DB_ECHO}
if "sqlite" in db_url_str:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_pre_ping": True,
        "poolclass": NullPool if settings.ENVIRONMENT == "test" else None,
    })

# Create async engine
engine = create_async_engine(db_url_str, **engine_kwargs)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
async_session_factory = AsyncSessionLocal



async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    
    Yields:
        AsyncSession: Database session
        
    Usage:
        @app.get("/items")
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


async def init_db() -> None:
    """
    Initialize database connection.
    Called during application startup.
    """
    try:
        async with engine.begin() as conn:
            if "sqlite" in db_url_str:
                from app.db.base import Base
                await conn.run_sync(Base.metadata.create_all)
            else:
                await conn.execute(text("SELECT 1"))
        logger.info("database_connected", url=db_url_str.split("@")[-1])
    except Exception as e:
        logger.warning("database_connection_failed_local_mode", error=str(e))



async def close_db() -> None:
    """
    Close database connection.
    Called during application shutdown.
    """
    await engine.dispose()
    logger.info("database_connection_closed")
