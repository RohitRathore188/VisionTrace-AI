"""
Application Configuration
Pydantic Settings for environment variable management
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All settings are typed and validated using Pydantic.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "VisionTrace AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    API_V1_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    RELOAD: bool = False
    
    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    # Database
    DATABASE_URL: Union[PostgresDsn, str] = Field(
        ...,
        description="PostgreSQL connection string"
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string"
    )
    REDIS_DECODE_RESPONSES: bool = True
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_STORAGE_URL: Optional[str] = None  # Defaults to REDIS_URL
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    LOG_FORMAT: str = "json"  # json or console
    LOG_FILE: Optional[str] = None
    
    # Sentry
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: Optional[str] = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    
    # Supabase
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_ANON_KEY: str = Field(..., description="Supabase anon/public key")
    SUPABASE_SERVICE_KEY: str = Field(..., description="Supabase service role key")
    SUPABASE_JWT_SECRET: str = Field(..., description="Supabase JWT secret")
    
    # Supabase Storage
    SUPABASE_STORAGE_BUCKET_VIDEOS: str = "videos"
    SUPABASE_STORAGE_BUCKET_FRAMES: str = "frames"
    
    # File Upload
    MAX_VIDEO_SIZE_MB: int = 2048
    ALLOWED_VIDEO_EXTENSIONS: List[str] = [".mp4", ".avi", ".mov", ".mkv"]
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp"]
    
    # AI Models
    YOLO_MODEL: str = "yolov8n.pt"
    OPENCLIP_MODEL: str = "ViT-B-32"
    OPENCLIP_PRETRAINED: str = "laion2b_s34b_b79k"
    
    # FAISS
    FAISS_INDEX_PATH: str = Field(
        default="./data/faiss_indexes/visiontrace_512d.index",
        description="Path to store FAISS index files"
    )
    
    # Celery
    CELERY_BROKER_URL: Optional[str] = None  # Defaults to REDIS_URL
    CELERY_RESULT_BACKEND: Optional[str] = None  # Defaults to REDIS_URL
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 3600  # 1 hour
    
    @field_validator("RATE_LIMIT_STORAGE_URL", mode="before")
    @classmethod
    def set_rate_limit_storage_url(cls, v: Optional[str], info) -> str:
        if v is None:
            return info.data.get("REDIS_URL", "redis://localhost:6379/0")
        return v
    
    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def set_celery_broker_url(cls, v: Optional[str], info) -> str:
        if v is None:
            return info.data.get("REDIS_URL", "redis://localhost:6379/0")
        return v
    
    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def set_celery_result_backend(cls, v: Optional[str], info) -> str:
        if v is None:
            return info.data.get("REDIS_URL", "redis://localhost:6379/0")
        return v
    
    @field_validator("SENTRY_ENVIRONMENT", mode="before")
    @classmethod
    def set_sentry_environment(cls, v: Optional[str], info) -> Optional[str]:
        if v is None:
            return info.data.get("ENVIRONMENT")
        return v
    
    @property
    def database_url_sync(self) -> str:
        """Synchronous database URL for Alembic migrations"""
        return str(self.DATABASE_URL).replace("+asyncpg", "")
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS middleware configuration"""
        return {
            "allow_origins": self.ALLOWED_ORIGINS,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }


# Global settings instance
settings = Settings()
