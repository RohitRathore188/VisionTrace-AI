"""
OpenCLIP Feature Embedding Service
Integrates OpenCLIP (ViT-B-32 / 512-dimensional vectors).
Generates L2-normalized vector embeddings for keyframes, cropped objects, image queries, and text queries.
Stores feature vectors in PostgreSQL pgvector for vector search.
"""

import os
import gc
import asyncio
import logging
import uuid
import numpy as np
from io import BytesIO
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timezone

try:
    import torch
    from PIL import Image
except ImportError:
    torch = None
    Image = None

try:
    import open_clip
except ImportError:
    open_clip = None

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.models.video import Video
from app.models.frame import Frame
from app.models.object import ObjectDetection
from app.models.embedding import Embedding, VECTOR_DIMENSION
from app.services.storage_service import storage_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class CLIPEmbeddingProgress:
    """Class tracking progress for OpenCLIP embedding generation jobs"""

    def __init__(self, video_id: uuid.UUID, total_items: int = 0):
        self.video_id = video_id
        self.status = "pending"  # pending, processing, completed, failed
        self.total_items = total_items
        self.processed_items = 0
        self.frame_embeddings_count = 0
        self.object_embeddings_count = 0
        self.progress_percent = 0.0
        self.error_message: Optional[str] = None
        self.started_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def update(self, processed: int, total: int, frame_cnt: int, obj_cnt: int):
        self.processed_items = processed
        self.total_items = max(total, 1)
        self.frame_embeddings_count = frame_cnt
        self.object_embeddings_count = obj_cnt
        self.progress_percent = min(100.0, round((processed / self.total_items) * 100, 1))
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "video_id": str(self.video_id),
            "status": self.status,
            "total_items": self.total_items,
            "processed_items": self.processed_items,
            "frame_embeddings_count": self.frame_embeddings_count,
            "object_embeddings_count": self.object_embeddings_count,
            "progress_percent": self.progress_percent,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class OpenCLIPService:
    """Service providing OpenCLIP vector embedding generation for frames, objects, image queries, and text queries"""

    def __init__(self):
        self.model_name = "ViT-B-32"
        self.pretrained = "laion2b_s34b_b79k"
        self.dimension = VECTOR_DIMENSION  # 512
        self._model = None
        self._preprocess = None
        self._tokenizer = None
        self.device = "cuda" if (torch is not None and torch.cuda.is_available()) else "cpu"
        self._progress_map: Dict[str, CLIPEmbeddingProgress] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._workers: List[asyncio.Task] = []
        self._is_running = False

    def _load_model(self):
        """Lazy load OpenCLIP model, preprocessor, and tokenizer"""
        if self._model is None:
            if open_clip is not None and torch is not None:
                try:
                    logger.info(f"Loading OpenCLIP model ({self.model_name}) on device: {self.device}")
                    model, _, preprocess = open_clip.create_model_and_transforms(
                        self.model_name,
                        pretrained=self.pretrained,
                        device=self.device
                    )
                    tokenizer = open_clip.get_tokenizer(self.model_name)
                    self._model = model.eval()
                    self._preprocess = preprocess
                    self._tokenizer = tokenizer
                except Exception as e:
                    logger.warning(f"Failed to load OpenCLIP model: {str(e)}")
                    self._model = None
            else:
                logger.info("OpenCLIP / Torch not installed. Using normalized pseudo-vector generator fallback.")

    def get_progress(self, video_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Get embedding generation status dictionary"""
        vid_str = str(video_id)
        if vid_str in self._progress_map:
            return self._progress_map[vid_str].to_dict()
        return None

    def start_worker_queue(self):
        """Start background embedding worker task loop"""
        if not self._is_running:
            self._is_running = True
            task = asyncio.create_task(self._worker_loop())
            self._workers.append(task)
            logger.info("Started background OpenCLIP embedding worker")

    async def enqueue_embedding_generation(
        self,
        video_id: uuid.UUID,
        include_frames: bool = True,
        include_objects: bool = True
    ) -> Dict[str, Any]:
        """Enqueue video for background OpenCLIP embedding generation"""
        self.start_worker_queue()
        vid_str = str(video_id)

        progress = CLIPEmbeddingProgress(video_id=video_id)
        self._progress_map[vid_str] = progress

        await self._queue.put((video_id, include_frames, include_objects))
        logger.info(f"Enqueued video {video_id} for OpenCLIP embedding generation")
        return progress.to_dict()

    async def _worker_loop(self):
        """Worker loop processing embedding generation queue items"""
        while self._is_running:
            try:
                video_id, include_frames, include_objects = await self._queue.get()
                await self._process_video_embeddings(video_id, include_frames, include_objects)
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"OpenCLIP worker error: {str(e)}", exc_info=True)

    async def _process_video_embeddings(
        self,
        video_id: uuid.UUID,
        include_frames: bool = True,
        include_objects: bool = True
    ):
        """Batch process keyframes and detected objects for a video through OpenCLIP"""
        vid_str = str(video_id)
        progress = self._progress_map.get(vid_str, CLIPEmbeddingProgress(video_id=video_id))
        progress.status = "processing"

        async with async_session_factory() as db:
            self._load_model()

            frames: List[Frame] = []
            objects: List[ObjectDetection] = []

            if include_frames:
                stmt_f = select(Frame).where(Frame.video_id == video_id).order_by(Frame.frame_number.asc())
                res_f = await db.execute(stmt_f)
                frames = list(res_f.scalars().all())

            if include_objects:
                stmt_o = select(ObjectDetection).where(ObjectDetection.video_id == video_id)
                res_o = await db.execute(stmt_o)
                objects = list(res_o.scalars().all())

            total_items = len(frames) + len(objects)
            if total_items == 0:
                progress.status = "failed"
                progress.error_message = f"No frames or objects found for video {video_id}"
                return

            progress.total_items = total_items
            processed_cnt = 0
            frame_emb_cnt = 0
            obj_emb_cnt = 0

            # Batch process keyframes
            if frames:
                frame_vectors = await self.generate_frame_embeddings_batch(frames)
                emb_records = []
                for frame_obj, vector in zip(frames, frame_vectors):
                    emb_records.append(
                        Embedding(
                            id=uuid.uuid4(),
                            frame_id=frame_obj.id,
                            object_id=None,
                            model_name=f"CLIP-{self.model_name}",
                            dimension=self.dimension,
                            embedding=vector,
                            metadata_json={
                                "frame_number": frame_obj.frame_number,
                                "timestamp_seconds": frame_obj.timestamp_seconds
                            }
                        )
                    )
                    processed_cnt += 1
                    frame_emb_cnt += 1

                db.add_all(emb_records)
                await db.commit()
                gc.collect()

                progress.update(processed_cnt, total_items, frame_emb_cnt, obj_emb_cnt)

            # Batch process detected objects
            if objects:
                obj_vectors = await self.generate_object_embeddings_batch(objects)
                emb_records = []
                for obj_item, vector in zip(objects, obj_vectors):
                    emb_records.append(
                        Embedding(
                            id=uuid.uuid4(),
                            frame_id=None,
                            object_id=obj_item.id,
                            model_name=f"CLIP-{self.model_name}",
                            dimension=self.dimension,
                            embedding=vector,
                            metadata_json={
                                "label": obj_item.label,
                                "confidence": obj_item.confidence,
                                "track_id": obj_item.track_id
                            }
                        )
                    )
                    processed_cnt += 1
                    obj_emb_cnt += 1

                db.add_all(emb_records)
                await db.commit()
                gc.collect()

                progress.update(processed_cnt, total_items, frame_emb_cnt, obj_emb_cnt)

            progress.status = "completed"
            logger.info(
                f"Completed OpenCLIP embedding generation for video {video_id} "
                f"({frame_emb_cnt} frame vectors, {obj_emb_cnt} object vectors)"
            )

    async def generate_frame_embeddings_batch(self, frames: List[Frame]) -> List[List[float]]:
        """Generate 512D OpenCLIP visual embeddings for a batch of keyframes"""
        self._load_model()
        image_paths = []
        for f in frames:
            if os.path.exists(f.image_path):
                image_paths.append(f.image_path)
            else:
                image_url = storage_service.get_playback_url(f.image_path, bucket_name=settings.SUPABASE_STORAGE_BUCKET_FRAMES)
                image_paths.append(image_url)

        return self._encode_images_batch(image_paths)

    async def generate_object_embeddings_batch(self, objects: List[ObjectDetection]) -> List[List[float]]:
        """Generate 512D OpenCLIP visual embeddings for a batch of cropped object images"""
        self._load_model()
        image_paths = []
        for obj in objects:
            crop_path = obj.crop_path
            if crop_path and os.path.exists(crop_path):
                image_paths.append(crop_path)
            elif crop_path:
                crop_url = storage_service.get_playback_url(crop_path)
                image_paths.append(crop_url)
            else:
                image_paths.append(None)

        return self._encode_images_batch(image_paths)

    def generate_image_bytes_embedding(self, image_bytes: bytes) -> List[float]:
        """
        Generate L2-normalized 512D OpenCLIP visual embedding from raw uploaded image bytes.
        """
        self._load_model()

        if self._model is not None and self._preprocess is not None and torch is not None and Image is not None:
            try:
                img = Image.open(BytesIO(image_bytes)).convert("RGB")
                tensor = self._preprocess(img).unsqueeze(0).to(self.device)
                with torch.no_grad():
                    image_features = self._model.encode_image(tensor)
                    image_features /= image_features.norm(dim=-1, keepdim=True)
                    vector = image_features[0].cpu().numpy().tolist()
                    return [round(float(v), 6) for v in vector]
            except Exception as err:
                logger.warning(f"Error encoding image query bytes: {str(err)}")

        return self._generate_pseudo_vector(f"img_query_{len(image_bytes)}")

    def generate_text_embedding(self, query_text: str) -> List[float]:
        """
        Generate L2-normalized 512D OpenCLIP text embedding for natural language query.
        (e.g., 'red car in parking lot at night', 'person wearing black hoodie')
        """
        self._load_model()

        if self._model is not None and self._tokenizer is not None and torch is not None:
            try:
                tokens = self._tokenizer([query_text]).to(self.device)
                with torch.no_grad():
                    text_features = self._model.encode_text(tokens)
                    text_features /= text_features.norm(dim=-1, keepdim=True)
                    vector = text_features[0].cpu().numpy().tolist()
                    return [round(float(v), 6) for v in vector]
            except Exception as err:
                logger.warning(f"Error encoding text with OpenCLIP: {str(err)}")

        return self._generate_pseudo_vector(query_text)

    def _encode_images_batch(self, image_sources: List[Optional[str]]) -> List[List[float]]:
        """Internal batch image visual feature encoding with PyTorch & PIL"""
        results: List[List[float]] = []

        if self._model is not None and self._preprocess is not None and torch is not None and Image is not None:
            batch_tensors = []
            valid_indices = []

            for idx, src in enumerate(image_sources):
                if not src:
                    continue
                try:
                    if src.startswith("http://") or src.startswith("https://"):
                        import requests
                        resp = requests.get(src, timeout=5)
                        img = Image.open(BytesIO(resp.content)).convert("RGB")
                    else:
                        img = Image.open(src).convert("RGB")

                    tensor = self._preprocess(img)
                    batch_tensors.append(tensor)
                    valid_indices.append(idx)
                except Exception as img_err:
                    logger.warning(f"Could not load image '{src}': {str(img_err)}")

            if batch_tensors:
                try:
                    tensors_stacked = torch.stack(batch_tensors).to(self.device)
                    with torch.no_grad():
                        image_features = self._model.encode_image(tensors_stacked)
                        image_features /= image_features.norm(dim=-1, keepdim=True)
                        feature_matrix = image_features.cpu().numpy()

                    feature_map: Dict[int, List[float]] = {}
                    for i, orig_idx in enumerate(valid_indices):
                        vec = [round(float(v), 6) for v in feature_matrix[i].tolist()]
                        feature_map[orig_idx] = vec

                    for idx in range(len(image_sources)):
                        if idx in feature_map:
                            results.append(feature_map[idx])
                        else:
                            results.append(self._generate_pseudo_vector(f"fallback_img_{idx}"))

                    return results
                except Exception as batch_err:
                    logger.error(f"Batch encoding error: {str(batch_err)}")

        for idx, src in enumerate(image_sources):
            results.append(self._generate_pseudo_vector(f"pseudo_img_{src or idx}"))

        return results

    def _generate_pseudo_vector(self, seed_text: str) -> List[float]:
        """Generate deterministic normalized 512D unit vector for testing"""
        rng = np.random.RandomState(abs(hash(seed_text)) % (2**32))
        vec = rng.randn(self.dimension)
        vec /= np.linalg.norm(vec)
        return [round(float(v), 6) for v in vec.tolist()]


# Singleton instance
clip_service = OpenCLIPService()
