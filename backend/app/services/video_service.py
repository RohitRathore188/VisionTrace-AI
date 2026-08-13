"""
Video Service
Business logic layer for video upload initialization, chunked uploads, metadata updates, and status tracking
"""

import os
import uuid
import math
import logging
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.video import Video, VideoStatus
from app.schemas.video import (
    VideoUploadInitRequest,
    VideoUploadInitResponse,
    VideoUploadCompleteRequest,
    VideoResponse,
)
from app.services.storage_service import storage_service
from app.core.config import settings

logger = logging.getLogger(__name__)

# Temporary directory for chunk assembly fallback
TEMP_CHUNK_DIR = os.path.join(os.getcwd(), "tmp_video_chunks")
os.makedirs(TEMP_CHUNK_DIR, exist_ok=True)


class VideoService:
    """Service providing video file management, metadata storage, and status tracking"""

    async def init_upload(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        payload: VideoUploadInitRequest
    ) -> Tuple[Video, VideoUploadInitResponse]:
        """
        Initialize video upload session and create pending video database record.
        """
        # Validate extension
        ext = os.path.splitext(payload.filename)[1].lower()
        if ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
            raise ValueError(f"Unsupported video format: {ext}. Allowed: {', '.join(settings.ALLOWED_VIDEO_EXTENSIONS)}")

        # Validate max size
        max_bytes = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024
        if payload.file_size_bytes > max_bytes:
            raise ValueError(f"File size exceeds maximum allowed limit of {settings.MAX_VIDEO_SIZE_MB}MB")

        video_id = uuid.uuid4()
        storage_path = storage_service.generate_storage_path(user_id, video_id, payload.filename)

        # Create database record in PENDING state
        video = Video(
            id=video_id,
            user_id=user_id,
            title=payload.title,
            description=payload.description,
            file_path=storage_path,
            file_size_bytes=payload.file_size_bytes,
            mime_type=payload.mime_type,
            duration_seconds=payload.duration_seconds,
            fps=payload.fps,
            width=payload.width,
            height=payload.height,
            status=VideoStatus.PENDING,
            metadata_json=payload.metadata_json or {}
        )

        db.add(video)
        await db.commit()
        await db.refresh(video)

        # Generate signed upload info from Supabase Storage
        upload_info = storage_service.get_signed_upload_url(storage_path)

        response = VideoUploadInitResponse(
            video_id=video.id,
            upload_url=upload_info.get("upload_url"),
            storage_path=storage_path,
            bucket_name=settings.SUPABASE_STORAGE_BUCKET_VIDEOS,
            chunk_size=5 * 1024 * 1024,
            resumable=True
        )

        return video, response

    async def handle_chunk_upload(
        self,
        db: AsyncSession,
        video_id: uuid.UUID,
        chunk_index: int,
        total_chunks: int,
        chunk_bytes: bytes
    ) -> Dict[str, Any]:
        """
        Handle chunk upload for chunked/resumable fallback uploading.
        Assembles chunks on storage when last chunk arrives.
        """
        video = await self.get_video_by_id(db, video_id)
        if not video:
            raise ValueError("Video record not found")

        chunk_dir = os.path.join(TEMP_CHUNK_DIR, str(video_id))
        os.makedirs(chunk_dir, exist_ok=True)
        chunk_file = os.path.join(chunk_dir, f"chunk_{chunk_index:05d}.part")

        with open(chunk_file, "wb") as f:
            f.write(chunk_bytes)

        # Check existing chunks
        uploaded_chunks = [f for f in os.listdir(chunk_dir) if f.endswith(".part")]
        is_complete = len(uploaded_chunks) >= total_chunks

        total_bytes_received = sum(os.path.getsize(os.path.join(chunk_dir, f)) for f in uploaded_chunks)

        if is_complete:
            # Reassemble file and upload to Supabase Storage
            final_temp_path = os.path.join(chunk_dir, "assembled_video.mp4")
            with open(final_temp_path, "wb") as outfile:
                for idx in range(total_chunks):
                    part_file = os.path.join(chunk_dir, f"chunk_{idx:05d}.part")
                    if os.path.exists(part_file):
                        with open(part_file, "rb") as infile:
                            outfile.write(infile.read())
                        os.remove(part_file)

            with open(final_temp_path, "rb") as final_file:
                assembled_data = final_file.read()
                storage_service.upload_file_bytes(video.file_path, assembled_data, video.mime_type)

            # Cleanup temp folder
            try:
                os.remove(final_temp_path)
                os.rmdir(chunk_dir)
            except Exception:
                pass

            # Mark as completed
            video.status = VideoStatus.COMPLETED
            await db.commit()

        return {
            "video_id": video.id,
            "chunk_index": chunk_index,
            "total_chunks": total_chunks,
            "bytes_received": len(chunk_bytes),
            "total_bytes_received": total_bytes_received,
            "is_complete": is_complete
        }

    async def complete_upload(
        self,
        db: AsyncSession,
        video_id: uuid.UUID,
        payload: VideoUploadCompleteRequest
    ) -> Video:
        """
        Finalize video upload, extract technical metadata with OpenCV, generate preview thumbnail,
        and enqueue background AI processing pipeline.
        """
        from app.services.frame_extractor import frame_extraction_service

        video = await self.get_video_by_id(db, video_id)
        if not video:
            raise ValueError("Video record not found")

        # Resolve local disk file path for OpenCV metadata extraction
        video.file_path = payload.file_path
        possible_paths = [
            payload.file_path,
            os.path.join(os.getcwd(), payload.file_path),
            os.path.join(os.getcwd(), "data", "videos", payload.file_path),
            os.path.join(os.getcwd(), "backend", "data", "videos", payload.file_path),
        ]
        
        video_src = payload.file_path
        for p in possible_paths:
            if os.path.exists(p):
                video_src = p
                break

        # Calculate file size from disk if available
        if os.path.exists(video_src):
            real_size = os.path.getsize(video_src)
            if real_size > 0:
                video.file_size_bytes = real_size

        # Extract technical video metadata and preview thumbnail with OpenCV
        try:
            import cv2
            cap = cv2.VideoCapture(video_src)
            if cap.isOpened():
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
                fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720
                duration = total_frames / fps if fps > 0 else 0.0

                video.fps = round(fps, 2)
                video.width = width
                video.height = height
                video.total_frames = total_frames
                video.duration_seconds = round(duration, 2)

                # Extract Preview Thumbnail at ~1.0 second mark
                target_thumb_frame = min(int(fps * 1.0), total_frames - 1)
                cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, target_thumb_frame))
                ret, frame = cap.read()
                if ret and frame is not None:
                    frame_dir = os.path.join(os.getcwd(), "data", "frames", str(video_id))
                    os.makedirs(frame_dir, exist_ok=True)
                    thumb_path = os.path.join(frame_dir, "thumbnail.jpg")
                    cv2.imwrite(thumb_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])

                    thumb_url = f"http://localhost:8000/data/frames/{video_id}/thumbnail.jpg"
                    if not video.metadata_json:
                        video.metadata_json = {}
                    video.metadata_json["thumbnail_url"] = thumb_url
                
                cap.release()
            else:
                logger.warning(f"OpenCV could not open video source for metadata: {video_src}")
        except Exception as err:
            logger.warning(f"Metadata / thumbnail extraction warning for video {video_id}: {err}")

        # Ensure values are not zero if payload provides them
        if not video.file_size_bytes and payload.file_size_bytes > 0:
            video.file_size_bytes = payload.file_size_bytes
        if not video.duration_seconds and payload.duration_seconds:
            video.duration_seconds = payload.duration_seconds

        # Update metadata_json payload if provided
        if payload.metadata_json:
            if not video.metadata_json:
                video.metadata_json = {}
            video.metadata_json.update(payload.metadata_json)

        video.status = VideoStatus.PROCESSING
        video.error_message = None

        await db.commit()
        await db.refresh(video)

        # Enqueue background pipeline: OpenCV Keyframe Extraction -> YOLO -> OpenCLIP Embeddings -> FAISS Index Sync
        try:
            await frame_extraction_service.enqueue_extraction(video_id=video.id, interval_seconds=1.0)
            logger.info(f"Automatically enqueued background AI processing pipeline for video {video.id}")
        except Exception as e:
            logger.error(f"Failed to enqueue background processing for video {video.id}: {e}")

        return video

    async def get_video_by_id(self, db: AsyncSession, video_id: uuid.UUID) -> Optional[Video]:
        """Fetch video record by UUID"""
        stmt = select(Video).where(Video.id == video_id, Video.deleted_at.is_(None))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_videos(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        status: Optional[VideoStatus] = None
    ) -> Tuple[List[Video], int]:
        """List videos for user with pagination and optional status filtering"""
        try:
            query = select(Video).where(Video.user_id == user_id, Video.deleted_at.is_(None))
            count_query = select(func.count(Video.id)).where(Video.user_id == user_id, Video.deleted_at.is_(None))

            if status:
                query = query.where(Video.status == status)
                count_query = count_query.where(Video.status == status)

            total_result = await db.execute(count_query)
            total = total_result.scalar_one()

            offset = (page - 1) * page_size
            query = query.order_by(desc(Video.created_at)).offset(offset).limit(page_size)

            result = await db.execute(query)
            videos = list(result.scalars().all())

            return videos, total
        except Exception as err:
            logger.warning(f"Database query fallback in list_videos: {err}")
            return [], 0

    async def delete_video(self, db: AsyncSession, video_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Soft delete video and remove file from Supabase storage"""
        video = await self.get_video_by_id(db, video_id)
        if not video or video.user_id != user_id:
            return False

        # Soft delete record
        video.soft_delete()
        await db.commit()

        # Delete asset from Supabase Storage asynchronously
        storage_service.delete_file(video.file_path)
        return True

    def format_video_response(self, video: Video) -> VideoResponse:
        """Format video database model into VideoResponse with playback URL and thumbnail URL"""
        playback_url = storage_service.get_playback_url(video.file_path)
        thumb_url = None
        if video.metadata_json and isinstance(video.metadata_json, dict):
            thumb_url = video.metadata_json.get("thumbnail_url")
        if not thumb_url:
            for p in [
                os.path.join(os.getcwd(), "data", "frames", str(video.id), "thumbnail.jpg"),
                os.path.join(os.getcwd(), "data", "frames", str(video.id), "frame_000000.jpg"),
                os.path.join(os.getcwd(), "data", "frames", str(video.id), "frame_000060.jpg"),
                os.path.join(os.getcwd(), "data", "frames", str(video.id), "frame_000360.jpg"),
                os.path.join(os.path.dirname(os.getcwd()), "data", "frames", str(video.id), "thumbnail.jpg"),
            ]:
                if os.path.exists(p):
                    thumb_url = f"http://localhost:8000/data/frames/{video.id}/{os.path.basename(p)}"
                    break

        return VideoResponse(
            id=video.id,
            user_id=video.user_id,
            title=video.title,
            description=video.description,
            file_path=video.file_path,
            file_size_bytes=video.file_size_bytes,
            mime_type=video.mime_type,
            duration_seconds=video.duration_seconds,
            fps=video.fps,
            width=video.width,
            height=video.height,
            total_frames=video.total_frames,
            status=video.status,
            error_message=video.error_message,
            metadata_json=video.metadata_json or {},
            created_at=video.created_at,
            updated_at=video.updated_at,
            playback_url=playback_url,
            thumbnail_url=thumb_url
        )


# Singleton instance
video_service = VideoService()
