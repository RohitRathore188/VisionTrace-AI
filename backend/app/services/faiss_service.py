"""
FAISS (Facebook AI Similarity Search) Service
Creates 512D vector index (IndexFlatIP / HNSW), stores OpenCLIP embeddings,
persists index binary files, and executes high-speed Top-K similarity search with score ranking.
"""

import os
import logging
import uuid
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timezone

try:
    import faiss
except ImportError:
    faiss = None

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.session import async_session_factory
from app.models.embedding import Embedding, VECTOR_DIMENSION
from app.models.frame import Frame
from app.models.object import ObjectDetection
from app.models.video import Video
from app.services.storage_service import storage_service
from app.services.clip_service import clip_service
from app.core.config import settings

logger = logging.getLogger(__name__)

# FAISS Index Storage Directory
FAISS_DIR = os.path.join(os.getcwd(), "data", "faiss_indexes")
os.makedirs(FAISS_DIR, exist_ok=True)
FAISS_INDEX_FILE = os.path.join(FAISS_DIR, "visiontrace_512d.index")


class FAISSService:
    """Service providing FAISS vector index management, embedding storage, and Top-K similarity search"""

    def __init__(self):
        self.dimension = VECTOR_DIMENSION  # 512
        self.index_file = FAISS_INDEX_FILE
        self._index = None
        self._metadata_map: Dict[int, Dict[str, Any]] = {}  # numeric_id -> metadata
        self._next_id = 1
        self._is_initialized = False

    def _init_index(self):
        """Initialize or load FAISS IndexFlatIP (Inner Product = Cosine Similarity for unit vectors)"""
        if self._is_initialized:
            return

        if faiss is not None:
            try:
                if os.path.exists(self.index_file):
                    logger.info(f"Loading FAISS index from: {self.index_file}")
                    self._index = faiss.read_index(self.index_file)
                else:
                    logger.info(f"Creating new FAISS 512D IndexFlatIP")
                    base_index = faiss.IndexFlatIP(self.dimension)
                    self._index = faiss.IndexIDMap2(base_index)
            except Exception as e:
                logger.warning(f"Error initializing FAISS index: {str(e)}")
                self._index = None
        else:
            logger.info("FAISS library not installed. Operating with high-speed NumPy cosine similarity engine.")

        self._is_initialized = True

    def save_index(self):
        """Persist FAISS index binary file to disk"""
        if faiss is not None and self._index is not None:
            try:
                faiss.write_index(self._index, self.index_file)
                logger.info(f"Persisted FAISS index binary to: {self.index_file}")
            except Exception as e:
                logger.error(f"Failed to save FAISS index: {str(e)}")

    def add_embeddings(
        self,
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Add batch of 512D embeddings and metadata to FAISS index.
        Returns assigned integer vector IDs.
        """
        self._init_index()

        if not vectors or len(vectors) == 0:
            return []

        np_vectors = np.array(vectors, dtype=np.float32)
        norms = np.linalg.norm(np_vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        np_vectors = np_vectors / norms

        assigned_ids = []
        for meta in metadatas:
            vector_id = self._next_id
            self._next_id += 1
            self._metadata_map[vector_id] = meta
            assigned_ids.append(vector_id)

        ids_array = np.array(assigned_ids, dtype=np.int64)

        if faiss is not None and self._index is not None:
            try:
                self._index.add_with_ids(np_vectors, ids_array)
                self.save_index()
            except Exception as err:
                logger.error(f"Error adding vectors to FAISS index: {str(err)}")

        return assigned_ids

    def search_top_k(
        self,
        query_vector: List[float],
        top_k: int = 10,
        video_id: Optional[uuid.UUID] = None,
        min_score: float = 0.0,
        query_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute similarity search against FAISS index.
        Returns Top-K matched records ranked by highest similarity score.
        """
        self._init_index()

        if not query_vector:
            return []

        q_np = np.array([query_vector], dtype=np.float32)
        norm = np.linalg.norm(q_np)
        if norm > 0:
            q_np = q_np / norm

        results = []

        if faiss is not None and self._index is not None and self._index.ntotal > 0:
            try:
                search_k = min(top_k * 10, max(self._index.ntotal, 1))
                scores, indices = self._index.search(q_np, search_k)

                for score, vec_id in zip(scores[0], indices[0]):
                    if vec_id == -1:
                        continue

                    raw_sim = float(score)
                    meta = self._metadata_map.get(int(vec_id), {})
                    if video_id and meta.get("video_id") != str(video_id):
                        continue

                    sim_score = self._compute_boosted_score(raw_sim, meta, query_text)
                    if sim_score < min_score:
                        continue

                    res_item = dict(meta)
                    res_item["similarity_score"] = round(sim_score, 4)
                    res_item["vector_id"] = int(vec_id)
                    results.append(res_item)

                results.sort(key=lambda x: x["similarity_score"], reverse=True)
                return results[:top_k]
            except Exception as err:
                logger.error(f"FAISS search error: {str(err)}")

        return self._fallback_numpy_search(q_np[0], top_k, video_id, min_score, query_text)

    def _compute_boosted_score(self, raw_sim: float, meta: Dict[str, Any], query_text: Optional[str]) -> float:
        """Boost similarity score if natural language query attributes match object labels"""
        score = max(0.0, min(1.0, raw_sim))
        if not query_text:
            return score

        q_lower = query_text.lower()
        obj_label = str(meta.get("label", "")).lower()

        # Attribute keyword matching boost
        keywords = ["person", "shirt", "man", "woman", "car", "vehicle", "truck", "backpack", "bag", "phone", "laptop", "bicycle", "bike", "animal"]
        for kw in keywords:
            if kw in q_lower:
                if (kw in obj_label) or (kw in ["car", "truck", "bicycle", "bike"] and obj_label == "vehicle") or (kw in ["backpack", "bag"] and obj_label == "bag"):
                    score = min(1.0, score + 0.12)
                    break

        return score

    def _fallback_numpy_search(
        self,
        q_vec: np.ndarray,
        top_k: int,
        video_id: Optional[uuid.UUID],
        min_score: float,
        query_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fallback cosine similarity search using NumPy matrix dot products"""
        if not self._metadata_map:
            return []

        candidates = []
        for vec_id, meta in self._metadata_map.items():
            if video_id and meta.get("video_id") != str(video_id):
                continue

            stored_vec = meta.get("vector")
            if stored_vec is not None:
                v_np = np.array(stored_vec, dtype=np.float32)
                v_norm = np.linalg.norm(v_np)
                if v_norm > 0:
                    v_np = v_np / v_norm

                raw_dot = float(np.dot(q_vec, v_np))
                score = self._compute_boosted_score(raw_dot, meta, query_text)
                if score >= min_score:
                    item = dict(meta)
                    item["similarity_score"] = round(score, 4)
                    item["vector_id"] = vec_id
                    candidates.append(item)

        candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
        return candidates[:top_k]

    async def build_index_from_db(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Build and synchronize FAISS index directly from PostgreSQL embeddings table.
        """
        stmt = (
            select(Embedding)
            .options(
                joinedload(Embedding.frame).joinedload(Frame.video),
                joinedload(Embedding.object).joinedload(ObjectDetection.frame)
            )
        )
        res = await db.execute(stmt)
        embeddings = list(res.scalars().all())

        if not embeddings:
            return {"status": "empty", "total_indexed": 0}

        vectors = []
        metadatas = []

        for emb in embeddings:
            if not emb.embedding:
                continue

            vec_list = [float(v) for v in emb.embedding]

            meta: Dict[str, Any] = {
                "embedding_id": str(emb.id),
                "model_name": emb.model_name,
                "vector": vec_list
            }

            if emb.frame:
                meta.update({
                    "type": "frame",
                    "frame_id": str(emb.frame.id),
                    "video_id": str(emb.frame.video_id),
                    "video_title": emb.frame.video.title if emb.frame.video else "Surveillance Video",
                    "frame_number": emb.frame.frame_number,
                    "timestamp_seconds": emb.frame.timestamp_seconds,
                    "image_url": storage_service.get_playback_url(emb.frame.image_path, bucket_name=settings.SUPABASE_STORAGE_BUCKET_FRAMES)
                })
            elif emb.object:
                frame_obj = emb.object.frame
                meta.update({
                    "type": "object",
                    "object_id": str(emb.object.id),
                    "frame_id": str(emb.object.frame_id),
                    "video_id": str(emb.object.video_id),
                    "label": emb.object.label,
                    "confidence": emb.object.confidence,
                    "bounding_box": emb.object.bounding_box,
                    "crop_url": storage_service.get_playback_url(emb.object.crop_path) if emb.object.crop_path else None,
                    "frame_number": frame_obj.frame_number if frame_obj else 0,
                    "timestamp_seconds": frame_obj.timestamp_seconds if frame_obj else 0.0,
                    "image_url": storage_service.get_playback_url(frame_obj.image_path, bucket_name=settings.SUPABASE_STORAGE_BUCKET_FRAMES) if frame_obj else None
                })

            vectors.append(vec_list)
            metadatas.append(meta)

        assigned_ids = self.add_embeddings(vectors, metadatas)

        total_indexed = self._index.ntotal if (faiss is not None and self._index is not None) else len(self._metadata_map)
        return {
            "status": "completed",
            "total_indexed": total_indexed,
            "dimension": self.dimension,
            "index_type": "IndexFlatIP"
        }

    def get_index_stats(self) -> Dict[str, Any]:
        """Get status & statistics for FAISS vector index"""
        total = self._index.ntotal if (faiss is not None and self._index is not None) else len(self._metadata_map)
        return {
            "total_vectors": total,
            "dimension": self.dimension,
            "index_type": "IndexFlatIP",
            "is_faiss_native": (faiss is not None and self._index is not None),
            "index_file": self.index_file
        }


# Singleton instance
faiss_service = FAISSService()
