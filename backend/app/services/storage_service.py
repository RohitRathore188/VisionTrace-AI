"""
Supabase Storage Service
Service for managing video file uploads, extracted keyframe images, signed URLs, and bucket assets in Supabase Storage
"""

import os
import uuid
import logging
from typing import Optional, Dict, Any
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseStorageService:
    """Service handling interactions with Supabase Storage buckets for videos and frames"""

    def __init__(self) -> None:
        """Initialize Supabase admin client using service key for storage operations"""
        self.supabase_url = settings.SUPABASE_URL
        self.service_key = settings.SUPABASE_SERVICE_KEY
        self.videos_bucket = settings.SUPABASE_STORAGE_BUCKET_VIDEOS
        self.frames_bucket = settings.SUPABASE_STORAGE_BUCKET_FRAMES
        self._client: Optional[Client] = None

    @property
    def client(self) -> Optional[Client]:
        """Lazy load Supabase client"""
        if self._client is None:
            try:
                self._client = create_client(self.supabase_url, self.service_key)
            except Exception as e:
                logger.warning(f"Could not initialize Supabase storage client: {str(e)}. Operating in local dev mode.")
                return None
        return self._client

    def ensure_bucket_exists(self, bucket_name: Optional[str] = None) -> None:
        """Ensure videos or frames bucket exists in Supabase Storage"""
        if not self.client:
            return
        target_bucket = bucket_name or self.videos_bucket
        try:
            buckets = self.client.storage.list_buckets()
            bucket_names = [b.name for b in buckets] if buckets else []
            if target_bucket not in bucket_names:
                logger.info(f"Creating Supabase Storage bucket: {target_bucket}")
                self.client.storage.create_bucket(
                    target_bucket,
                    options={"public": True, "file_size_limit": settings.MAX_VIDEO_SIZE_MB * 1024 * 1024}
                )
        except Exception as e:
            logger.warning(f"Storage bucket verification check warning for '{target_bucket}': {str(e)}")

    def generate_storage_path(self, user_id: uuid.UUID, video_id: uuid.UUID, filename: str) -> str:
        """Generate structured storage path: {user_id}/{video_id}/{filename}"""
        ext = os.path.splitext(filename)[1].lower() or ".mp4"
        clean_name = f"video_{video_id}{ext}"
        return f"{user_id}/{video_id}/{clean_name}"

    def generate_frame_storage_path(self, video_id: uuid.UUID, frame_number: int) -> str:
        """Generate storage path for extracted keyframe: {video_id}/frame_{frame_number:06d}.jpg"""
        return f"{video_id}/frame_{frame_number:06d}.jpg"

    def get_signed_upload_url(self, storage_path: str, bucket_name: Optional[str] = None, expires_in: int = 3600) -> Dict[str, Any]:
        """Generate a presigned upload URL for client direct uploading"""
        target_bucket = bucket_name or self.videos_bucket
        try:
            self.ensure_bucket_exists(target_bucket)
            res = self.client.storage.from_(target_bucket).create_signed_upload_url(storage_path)
            return {
                "upload_url": res.get("signedUrl") if isinstance(res, dict) else getattr(res, "signed_url", None),
                "path": storage_path,
                "token": res.get("token") if isinstance(res, dict) else getattr(res, "token", None)
            }
        except Exception as e:
            logger.error(f"Failed to generate signed upload URL: {str(e)}")
            return {
                "upload_url": f"{self.supabase_url}/storage/v1/object/{target_bucket}/{storage_path}",
                "path": storage_path,
                "token": None
            }

    def upload_file_bytes(
        self,
        storage_path: str,
        file_data: bytes,
        content_type: str = "video/mp4",
        bucket_name: Optional[str] = None
    ) -> str:
        """Upload raw bytes to Supabase Storage bucket"""
        target_bucket = bucket_name or self.videos_bucket
        self.ensure_bucket_exists(target_bucket)
        res = self.client.storage.from_(target_bucket).upload(
            path=storage_path,
            file=file_data,
            file_options={"content-type": content_type, "upsert": "true"}
        )
        return storage_path

    def get_playback_url(self, storage_path: str, bucket_name: Optional[str] = None, expires_in: int = 86400) -> str:
        """Get signed or public URL for video playback or keyframe preview"""
        target_bucket = bucket_name or self.videos_bucket
        try:
            public_url = self.client.storage.from_(target_bucket).get_public_url(storage_path)
            if public_url:
                return public_url
            
            signed_res = self.client.storage.from_(target_bucket).create_signed_url(storage_path, expires_in)
            if isinstance(signed_res, dict) and "signedUrl" in signed_res:
                return signed_res["signedUrl"]
            return f"{self.supabase_url}/storage/v1/object/public/{target_bucket}/{storage_path}"
        except Exception as e:
            logger.warning(f"Could not resolve public URL for {storage_path}: {str(e)}")
            return f"{self.supabase_url}/storage/v1/object/public/{target_bucket}/{storage_path}"

    def delete_file(self, storage_path: str, bucket_name: Optional[str] = None) -> bool:
        """Remove file from storage bucket"""
        target_bucket = bucket_name or self.videos_bucket
        try:
            self.client.storage.from_(target_bucket).remove([storage_path])
            return True
        except Exception as e:
            logger.error(f"Error deleting file from storage: {str(e)}")
            return False


# Singleton instance
storage_service = SupabaseStorageService()
