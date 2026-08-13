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
    import faiss  # type: ignore
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
        self._metadata_map: Dict[int, Dict[str, Any]] = {}  # numeric_id -> metadata (NO raw vector stored here)
        self._vectors_map: Dict[int, np.ndarray] = {}       # numeric_id -> numpy vector (for NumPy fallback)
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

    def reset(self):
        """
        Fully reset the FAISS index and metadata maps.
        Called before rebuilding from DB to avoid duplicate vectors.
        """
        self._metadata_map.clear()
        self._vectors_map.clear()
        self._next_id = 1
        self._index = None
        self._is_initialized = False
        # Delete old index file so we rebuild clean
        if os.path.exists(self.index_file):
            try:
                os.remove(self.index_file)
                logger.info(f"[FAISS RESET] Deleted stale index file: {self.index_file}")
            except Exception as e:
                logger.warning(f"[FAISS RESET] Could not delete index file: {e}")
        logger.info("[FAISS RESET] In-memory index and metadata cleared.")

    def add_embeddings(
        self,
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Add batch of 512D embeddings and metadata to FAISS index.
        Vectors are stored separately from metadata (no 'vector' key in metadata map).
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
        for i, meta in enumerate(metadatas):
            vector_id = self._next_id
            self._next_id += 1
            # Store metadata WITHOUT the raw vector (clean separation)
            clean_meta = {k: v for k, v in meta.items() if k != "vector"}
            self._metadata_map[vector_id] = clean_meta
            # Store the normalized vector separately for NumPy fallback
            self._vectors_map[vector_id] = np_vectors[i]
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
        video_ids: Optional[List[uuid.UUID]] = None,
        min_score: float = 0.0,
        query_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute similarity search against FAISS index.
        Returns Top-K matched records ranked by highest similarity score.
        Supports filtering by single video_id or list of video_ids.
        """
        self._init_index()

        if not query_vector:
            return []

        q_np = np.array([query_vector], dtype=np.float32)
        q_norm = np.linalg.norm(q_np)
        if q_norm > 0:
            q_np = q_np / q_norm

        # Build allowed video ID set for search scope filtering
        allowed_vids = set()
        if video_ids:
            allowed_vids = {str(vid) for vid in video_ids if vid}
        elif video_id:
            allowed_vids = {str(video_id)}

        # -- DEBUG: Embedding preview ------------------------------------------
        preview = q_np[0][:10].tolist()
        embedding_magnitude = float(np.linalg.norm(q_np[0]))
        index_size = self._index.ntotal if (faiss is not None and self._index is not None) else len(self._metadata_map)

        debug_header = (
            f"\n{'='*70}\n"
            f"[SEARCH DEBUG] Query Text   : '{query_text or 'visual_query'}'\n"
            f"[SEARCH DEBUG] Filter VIDs  : {list(allowed_vids) if allowed_vids else 'ALL'}\n"
            f"[SEARCH DEBUG] Embedding Dim: {len(query_vector)}\n"
            f"[SEARCH DEBUG] FAISS Size   : {index_size} vectors\n"
            f"{'='*70}"
        )
        logger.info(debug_header)
        print(debug_header, flush=True)

        results = []
        all_candidates = []

        if faiss is not None and self._index is not None and self._index.ntotal > 0:
            try:
                search_k = self._index.ntotal if allowed_vids else min(top_k * 10, max(self._index.ntotal, 1))
                scores, indices = self._index.search(q_np, search_k)

                for rank, (score, vec_id) in enumerate(zip(scores[0], indices[0])):
                    if vec_id == -1:
                        continue

                    raw_sim = float(score)
                    meta = self._metadata_map.get(int(vec_id), {})
                    if allowed_vids and meta.get("video_id") not in allowed_vids:
                        continue

                    sim_score = self._compute_boosted_score(raw_sim, meta, query_text)
                    res_item = dict(meta)
                    res_item["similarity_score"] = round(sim_score, 4)
                    res_item["raw_similarity"] = round(raw_sim, 4)
                    res_item["vector_id"] = int(vec_id)
                    all_candidates.append(res_item)

                    if sim_score >= min_score:
                        results.append(res_item)

                all_candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
                results.sort(key=lambda x: x["similarity_score"], reverse=True)

                # If threshold filtering yielded 0 results, return top candidates
                if not results and all_candidates:
                    logger.warning(
                        f"[THRESHOLD FALLBACK] Threshold min_score={min_score} yielded 0 results. "
                        f"Returning Top-{top_k} nearest candidates regardless of score threshold."
                    )
                    return all_candidates[:top_k]

                return results[:top_k]
            except Exception as err:
                logger.error(f"FAISS search error: {str(err)}", exc_info=True)

        return self._fallback_numpy_search(q_np[0], top_k, allowed_vids, min_score, query_text)

    def _compute_boosted_score(self, raw_sim: float, meta: Dict[str, Any], query_text: Optional[str]) -> float:
        """Boost similarity score if natural language query attributes match object labels"""
        score = max(0.0, min(1.0, raw_sim))
        if not query_text:
            return score

        q_lower = query_text.lower()
        obj_label = str(meta.get("label", "")).lower()

        # Attribute keyword matching boost
        keywords = ["person", "shirt", "man", "woman", "car", "vehicle", "truck", "bus", "van", "automobile", "motorcycle", "scooter", "backpack", "bag", "phone", "laptop", "bicycle", "bike", "animal"]
        vehicle_synonyms = ["car", "vehicle", "truck", "bus", "van", "automobile", "motorcycle", "scooter"]
        
        for kw in keywords:
            if kw in q_lower:
                if (kw in obj_label) or (kw in vehicle_synonyms and obj_label in ["vehicle", "car", "truck", "bus", "bicycle"]) or (kw in ["backpack", "bag"] and obj_label == "bag"):
                    score = min(1.0, score + 0.75)
                    break

        return score

    def _fallback_numpy_search(
        self,
        q_vec: np.ndarray,
        top_k: int,
        allowed_vids: set,
        min_score: float,
        query_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fallback cosine similarity search using NumPy matrix dot products.
        """
        if not self._vectors_map:
            logger.warning("[NUMPY FALLBACK] _vectors_map is empty - no vectors to search.")
            return []

        logger.info(f"[NUMPY FALLBACK] Searching {len(self._vectors_map)} vectors with NumPy dot products")
        vec_ids = list(self._vectors_map.keys())
        matrix = np.stack([self._vectors_map[vid] for vid in vec_ids], axis=0)
        scores = matrix @ q_vec

        candidates = []
        for i, vec_id in enumerate(vec_ids):
            meta = self._metadata_map.get(vec_id, {})
            if allowed_vids and meta.get("video_id") not in allowed_vids:
                continue

            raw_dot = float(scores[i])
            score = self._compute_boosted_score(raw_dot, meta, query_text)
            if score >= min_score:
                item = dict(meta)
                item["similarity_score"] = round(score, 4)
                item["raw_similarity"] = round(raw_dot, 4)
                item["vector_id"] = vec_id
                candidates.append(item)

        candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
        return candidates[:top_k]

    async def build_index_from_db(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Build and synchronize FAISS index directly from real database embeddings and frames.
        Always resets first to prevent duplicate/stale vectors.
        """
        from app.services.clip_service import clip_service

        # -- RESET before rebuild to guarantee clean state ---------------------
        self.reset()
        self._init_index()

        from sqlalchemy.orm import selectinload
        stmt = (
            select(Embedding)
            .options(
                joinedload(Embedding.frame).joinedload(Frame.video),
                joinedload(Embedding.frame).selectinload(Frame.objects),
                joinedload(Embedding.object).joinedload(ObjectDetection.frame)
            )
        )
        res = await db.execute(stmt)
        embeddings = list(res.scalars().all())

        if not embeddings:
            frame_stmt = select(Frame).options(joinedload(Frame.video))
            f_res = await db.execute(frame_stmt)
            frames = list(f_res.scalars().all())

            if frames:
                logger.info(f"[FAISS INDEX BUILD] Auto-generating real OpenCLIP visual embeddings for {len(frames)} frames")
                frame_vectors = await clip_service.generate_frame_embeddings_batch(frames)
                for fr, vec in zip(frames, frame_vectors):
                    emb = Embedding(
                        id=uuid.uuid4(),
                        frame_id=fr.id,
                        embedding=vec,
                        model_name=f"CLIP-{clip_service.model_name}",
                        dimension=clip_service.dimension
                    )
                    db.add(emb)
                await db.commit()
                res = await db.execute(stmt)
                embeddings = list(res.scalars().all())

        if not embeddings:
            logger.warning("[FAISS INDEX BUILD] No embeddings in DB and no frames found.")
            return {"status": "empty", "total_indexed": 0, "dimension": self.dimension, "index_type": "IndexFlatIP"}

        vectors = []
        metadatas = []

        for emb in embeddings:
            if not emb.embedding:
                continue

            raw_emb = emb.embedding
            if isinstance(raw_emb, (list, tuple)):
                vec_list = [float(v) for v in raw_emb]
            elif isinstance(raw_emb, str):
                import json
                vec_list = [float(v) for v in json.loads(raw_emb)]
            else:
                vec_list = [float(v) for v in list(raw_emb)]

            meta: Dict[str, Any] = {
                "embedding_id": str(emb.id),
                "model_name": emb.model_name,
            }

            if emb.frame:
                vid_obj = emb.frame.video
                cam_name = (vid_obj.metadata_json.get("camera_name") if vid_obj and vid_obj.metadata_json else None) or (vid_obj.title if vid_obj else "CAM-01 (Main Gate)")
                # Find primary object detection on this frame if available
                first_obj = (emb.frame.objects[0] if hasattr(emb.frame, "objects") and emb.frame.objects else None)
                meta.update({
                    "type": "frame",
                    "frame_id": str(emb.frame.id),
                    "video_id": str(emb.frame.video_id),
                    "video_title": vid_obj.title if vid_obj else "Surveillance Video",
                    "camera_name": cam_name,
                    "video_playback_url": storage_service.get_playback_url(vid_obj.file_path) if vid_obj else None,
                    "frame_number": emb.frame.frame_number,
                    "timestamp_seconds": emb.frame.timestamp_seconds,
                    "image_url": storage_service.get_playback_url(emb.frame.image_path, bucket_name=settings.SUPABASE_STORAGE_BUCKET_FRAMES),
                    "track_id": first_obj.track_id if first_obj else None,
                    "bounding_box": first_obj.bounding_box if first_obj else None,
                    "label": first_obj.label if first_obj else None,
                })
            elif emb.object:
                frame_obj = emb.object.frame
                vid_obj = frame_obj.video if frame_obj else None
                crop_path = emb.object.crop_path
                crop_bucket = settings.SUPABASE_STORAGE_BUCKET_CROPS if (crop_path and "crop" in crop_path) else settings.SUPABASE_STORAGE_BUCKET_FRAMES
                cam_name = (vid_obj.metadata_json.get("camera_name") if vid_obj and vid_obj.metadata_json else None) or (vid_obj.title if vid_obj else "CAM-01 (Main Gate)")
                meta.update({
                    "type": "object",
                    "object_id": str(emb.object.id),
                    "track_id": emb.object.track_id,
                    "frame_id": str(emb.object.frame_id),
                    "video_id": str(emb.object.video_id),
                    "label": emb.object.label,
                    "confidence": emb.object.confidence,
                    "bounding_box": emb.object.bounding_box,
                    "video_title": vid_obj.title if vid_obj else "Surveillance Video",
                    "camera_name": cam_name,
                    "video_playback_url": storage_service.get_playback_url(vid_obj.file_path) if vid_obj else None,
                    "crop_url": storage_service.get_playback_url(crop_path, bucket_name=crop_bucket) if crop_path else None,
                    "frame_number": frame_obj.frame_number if frame_obj else 0,
                    "timestamp_seconds": frame_obj.timestamp_seconds if frame_obj else 0.0,
                    "image_url": storage_service.get_playback_url(frame_obj.image_path, bucket_name=settings.SUPABASE_STORAGE_BUCKET_FRAMES) if frame_obj else None
                })

            vectors.append(vec_list)
            metadatas.append(meta)

        logger.info(f"[FAISS INDEX BUILD] Loaded {len(vectors)} embedding vectors from DB")
        print(f"[FAISS INDEX BUILD] Loaded {len(vectors)} embedding vectors from DB", flush=True)

        # Log embedding space diagnosis
        if vectors:
            sample = np.array(vectors[:min(5, len(vectors))], dtype=np.float32)
            norms = np.linalg.norm(sample, axis=1)
            logger.info(
                f"[FAISS INDEX BUILD] Sample vector norms: {norms.tolist()} "
                f"(should be ~1.0 for unit-normed CLIP vectors)"
            )
            print(
                f"[FAISS INDEX BUILD] Sample vector norms: {norms.tolist()}",
                flush=True
            )

        assigned_ids = self.add_embeddings(vectors, metadatas)

        total_indexed = self._index.ntotal if (faiss is not None and self._index is not None) else len(self._metadata_map)
        logger.info(f"[FAISS INDEX BUILD] Done. Total indexed: {total_indexed}")
        print(f"[FAISS INDEX BUILD] Done. Total indexed: {total_indexed}", flush=True)

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
