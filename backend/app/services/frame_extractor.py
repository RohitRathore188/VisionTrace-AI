"""
Frame Extraction Service
OpenCV-based high-performance video keyframe extraction with background worker queue,
progress tracking, memory optimization, retry policies, and metadata persistence.
"""

import os
import gc
import asyncio
import logging
import time
import uuid
import numpy as np
from typing import Optional, Dict, Any, List, Tuple, AsyncGenerator
from datetime import datetime, timezone

# Import OpenCV with fallback handling
try:
    import cv2
except ImportError:
    cv2 = None

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.models.video import Video, VideoStatus
from app.models.frame import Frame
from app.services.storage_service import storage_service
from app.core.config import settings

logger = logging.getLogger(__name__)

# Local fallback frame directory
LOCAL_FRAME_DIR = os.path.join(os.getcwd(), "data", "frames")
os.makedirs(LOCAL_FRAME_DIR, exist_ok=True)


class ExtractionProgress:
    """Class tracking progress state for a video frame extraction job"""

    def __init__(self, video_id: uuid.UUID, total_frames: int = 0):
        self.video_id = video_id
        self.status = "pending"  # pending, processing, completed, failed
        self.total_frames = total_frames
        self.processed_frames = 0
        self.extracted_count = 0
        self.progress_percent = 0.0
        self.current_timestamp = 0.0
        self.error_message: Optional[str] = None
        self.retry_count = 0
        self.max_retries = 3
        self.started_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def update(self, processed: int, total: int, extracted: int, timestamp: float):
        self.processed_frames = processed
        self.total_frames = max(total, 1)
        self.extracted_count = extracted
        self.current_timestamp = round(timestamp, 2)
        self.progress_percent = min(100.0, round((processed / self.total_frames) * 100, 1))
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "video_id": str(self.video_id),
            "status": self.status,
            "total_frames": self.total_frames,
            "processed_frames": self.processed_frames,
            "extracted_count": self.extracted_count,
            "progress_percent": self.progress_percent,
            "current_timestamp": self.current_timestamp,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class FrameExtractionService:
    """Service providing OpenCV frame extraction, interval calculation, and memory-managed streaming"""

    def __init__(self):
        self._progress_map: Dict[str, ExtractionProgress] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._workers: List[asyncio.Task] = []
        self._max_workers = 2
        self._is_running = False

    def get_progress(self, video_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Retrieve extraction progress dictionary for video ID"""
        vid_str = str(video_id)
        if vid_str in self._progress_map:
            return self._progress_map[vid_str].to_dict()
        return None

    def start_worker_queue(self):
        """Start background worker task loop"""
        if not self._is_running:
            self._is_running = True
            for i in range(self._max_workers):
                task = asyncio.create_task(self._worker_loop(i))
                self._workers.append(task)
            logger.info(f"Started {self._max_workers} background frame extraction workers")

    async def enqueue_extraction(
        self,
        video_id: uuid.UUID,
        interval_seconds: float = 1.0,
        jpeg_quality: int = 85
    ) -> Dict[str, Any]:
        """
        Enqueue a video for background frame extraction.
        """
        self.start_worker_queue()
        vid_str = str(video_id)

        progress = ExtractionProgress(video_id=video_id)
        self._progress_map[vid_str] = progress

        await self._queue.put((video_id, interval_seconds, jpeg_quality))
        logger.info(f"Enqueued video {video_id} for frame extraction (interval: {interval_seconds}s)")
        return progress.to_dict()

    async def _worker_loop(self, worker_id: int):
        """Background worker consuming extraction queue items"""
        logger.info(f"Worker {worker_id} ready for frame extraction tasks")
        while self._is_running:
            try:
                video_id, interval_seconds, jpeg_quality = await self._queue.get()
                logger.info(f"Worker {worker_id} processing video {video_id}")
                await self._process_video_extraction(video_id, interval_seconds, jpeg_quality)
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {str(e)}", exc_info=True)

    async def _process_video_extraction(
        self,
        video_id: uuid.UUID,
        interval_seconds: float = 1.0,
        jpeg_quality: int = 85
    ):
        """
        Process video frame extraction with exponential backoff retry policies.
        """
        vid_str = str(video_id)
        progress = self._progress_map.get(vid_str, ExtractionProgress(video_id=video_id))
        progress.status = "processing"

        async with async_session_factory() as db:
            # Fetch video record
            stmt = select(Video).where(Video.id == video_id, Video.deleted_at.is_(None))
            res = await db.execute(stmt)
            video = res.scalar_one_or_none()

            if not video:
                progress.status = "failed"
                progress.error_message = f"Video record {video_id} not found"
                return

            # Update video status to PROCESSING
            video.status = VideoStatus.PROCESSING
            await db.commit()

            # Attempt extraction with retry logic
            success = False
            while progress.retry_count <= progress.max_retries and not success:
                try:
                    await self._extract_frames_opencv(
                        db=db,
                        video=video,
                        interval_seconds=interval_seconds,
                        jpeg_quality=jpeg_quality,
                        progress=progress
                    )
                    success = True
                    progress.status = "completed"
                    video.status = VideoStatus.COMPLETED
                    video.total_frames = progress.total_frames
                    video.error_message = None
                    await db.commit()
                    logger.info(f"Successfully completed frame extraction for video {video_id} ({progress.extracted_count} frames)")
                except Exception as err:
                    progress.retry_count += 1
                    logger.warning(
                        f"Frame extraction attempt {progress.retry_count}/{progress.max_retries} failed for video {video_id}: {str(err)}"
                    )
                    if progress.retry_count > progress.max_retries:
                        progress.status = "failed"
                        progress.error_message = str(err)
                        video.status = VideoStatus.FAILED
                        video.error_message = f"Frame extraction failed: {str(err)}"
                        await db.commit()
                    else:
                        # Exponential backoff sleep before retry (1s, 2s, 4s...)
                        await asyncio.sleep(2 ** (progress.retry_count - 1))

    async def _extract_frames_opencv(
        self,
        db: AsyncSession,
        video: Video,
        interval_seconds: float,
        jpeg_quality: int,
        progress: ExtractionProgress
    ):
        """
        OpenCV streaming frame extraction engine.
        Optimized for low RAM usage by streaming frames and flushing batch DB commits.
        """
        if cv2 is None:
            raise RuntimeError("OpenCV (cv2) is not installed in the Python environment")

        # Resolve local or remote video path
        video_src = video.file_path
        if not os.path.exists(video_src):
            # Check if relative to working directory or fallback URL
            local_fallback = os.path.join(os.getcwd(), video.file_path)
            if os.path.exists(local_fallback):
                video_src = local_fallback

        cap = cv2.VideoCapture(video_src)
        if not cap.isOpened():
            # Try loading via presigned playback URL if file path is remote
            playback_url = storage_service.get_playback_url(video.file_path)
            cap = cv2.VideoCapture(playback_url)
            if not cap.isOpened():
                raise RuntimeError(f"OpenCV failed to open video source: {video.file_path}")

        try:
            # Video technical metadata
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1920
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 1080
            duration = total_frames / fps if fps > 0 else 0.0

            # Update video dimensions if not present
            video.fps = fps
            video.width = width
            video.height = height
            video.duration_seconds = duration

            progress.total_frames = total_frames

            # Calculate frame step interval (e.g., sample 1 frame every step frames)
            frame_step = max(1, int(round(fps * interval_seconds)))

            frame_number = 0
            extracted_count = 0
            frame_batch: List[Frame] = []
            BATCH_SIZE = 25  # Save batch of 25 frames per DB commit to optimize memory

            while cap.isOpened():
                # Stream grab next frame (lightweight without full decoding)
                grabbed = cap.grab()
                if not grabbed:
                    break

                # Process frame if matching step interval
                if frame_number % frame_step == 0:
                    ret, frame_bgr = cap.retrieve()
                    if not ret or frame_bgr is None:
                        frame_number += 1
                        continue

                    timestamp = round(frame_number / fps, 3)

                    # Calculate image quality metric (Laplacian variance for blur detection)
                    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
                    sharpness_score = round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 2)

                    # Encode frame as JPEG
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
                    ret_enc, jpeg_bytes = cv2.imencode(".jpg", frame_bgr, encode_param)
                    if not ret_enc:
                        frame_number += 1
                        continue

                    image_bytes = jpeg_bytes.tobytes()

                    # Save to Supabase Storage bucket 'frames'
                    frame_rel_path = storage_service.generate_frame_storage_path(video.id, frame_number)
                    try:
                        storage_service.upload_file_bytes(
                            storage_path=frame_rel_path,
                            file_data=image_bytes,
                            content_type="image/jpeg",
                            bucket_name=settings.SUPABASE_STORAGE_BUCKET_FRAMES
                        )
                        image_path = frame_rel_path
                    except Exception as storage_err:
                        logger.warning(f"Supabase frames upload fallback to local disk: {str(storage_err)}")
                        local_video_dir = os.path.join(LOCAL_FRAME_DIR, str(video.id))
                        os.makedirs(local_video_dir, exist_ok=True)
                        local_frame_path = os.path.join(local_video_dir, f"frame_{frame_number:06d}.jpg")
                        with open(local_frame_path, "wb") as f:
                            f.write(image_bytes)
                        image_path = local_frame_path

                    # Build Frame model
                    frame_obj = Frame(
                        id=uuid.uuid4(),
                        video_id=video.id,
                        frame_number=frame_number,
                        timestamp_seconds=timestamp,
                        image_path=image_path,
                        width=width,
                        height=height,
                        metadata_json={
                            "sharpness_score": sharpness_score,
                            "interval_seconds": interval_seconds,
                            "jpeg_quality": jpeg_quality,
                            "file_size_bytes": len(image_bytes)
                        }
                    )
                    frame_batch.append(frame_obj)
                    extracted_count += 1

                    # Commit batch to database and trigger garbage collection
                    if len(frame_batch) >= BATCH_SIZE:
                        db.add_all(frame_batch)
                        await db.commit()
                        frame_batch.clear()
                        gc.collect()

                frame_number += 1
                progress.update(
                    processed=frame_number,
                    total=total_frames,
                    extracted=extracted_count,
                    timestamp=frame_number / fps
                )

                # Yield control back to asyncio event loop periodically
                if frame_number % 10 == 0:
                    await asyncio.sleep(0.001)

            # Flush final batch
            if frame_batch:
                db.add_all(frame_batch)
                await db.commit()
                frame_batch.clear()
                gc.collect()

        finally:
            cap.release()
            cv2.destroyAllWindows()
            gc.collect()


# Singleton instance
frame_extraction_service = FrameExtractionService()
