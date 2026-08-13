"""
FastAPI Application Entry Point
Main application factory and configuration
"""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.middleware.error_handler import ErrorHandlerMiddleware
from app.api.middleware.logging import LoggingMiddleware
from app.api.middleware.request_id import RequestIDMiddleware
from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import close_db, init_db

# Configure structured logging
configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "application_startup",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT
    )
    
    # Initialize database
    await init_db()
    
    # Initialize Sentry (if configured)
    if settings.SENTRY_DSN:
        import sentry_sdk
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        )
        logger.info("sentry_initialized")
    
    yield
    
    # Shutdown
    logger.info("application_shutdown")
    await close_db()


def create_application() -> FastAPI:
    """
    Application factory.
    Creates and configures the FastAPI application instance.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Intelligent Video Search Platform",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )
    
    # Add middleware (order matters - first added = outermost)
    
    # 1. Error handling (outermost - catches all errors)
    app.add_middleware(ErrorHandlerMiddleware)
    
    # 2. CORS
    app.add_middleware(
        CORSMiddleware,
        **settings.get_cors_config()
    )
    
    # 3. Logging
    app.add_middleware(LoggingMiddleware)
    
    # 4. Request ID (innermost - runs first)
    app.add_middleware(RequestIDMiddleware)
    
    # Include routers
    app.include_router(api_router)
    
    # Mount Static Files for Local Media Storage
    from fastapi.staticfiles import StaticFiles
    import os
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    app.mount("/data", StaticFiles(directory=data_dir), name="data")
    
    # Root endpoint
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }
    
    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=1,
        log_config=None,  # Use our custom logging
    )
