import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def populate_accurate_detections():
    from app.db.session import async_session_factory
    from app.models.frame import Frame
    from app.models.object import ObjectDetection
    from app.models.embedding import Embedding
    from app.services.faiss_service import faiss_service
    from app.services.clip_service import clip_service
    from app.services.yolo_service import yolo_service
    from sqlalchemy import select, delete
    import uuid

    async with async_session_factory() as db:
        # Delete existing ObjectDetections and Embeddings
        await db.execute(delete(Embedding))
        await db.execute(delete(ObjectDetection))
        await db.commit()
        print("Cleared old ObjectDetections and Embeddings from DB.")

        # Get all frames
        f_res = await db.execute(select(Frame))
        frames = list(f_res.scalars().all())
        print(f"Processing {len(frames)} frames for category-aware detections...")

        # Generate Frame Embeddings
        frame_vectors = await clip_service.generate_frame_embeddings_batch(frames)
        for fr, vec in zip(frames, frame_vectors):
            emb = Embedding(
                id=uuid.uuid4(),
                frame_id=fr.id,
                object_id=None,
                embedding=vec,
                model_name=f"CLIP-{clip_service.model_name}",
                dimension=clip_service.dimension
            )
            db.add(emb)

        # Generate Object Detections & Embeddings
        new_objs = []
        for frame in frames:
            dets = await yolo_service.detect_objects_in_frame(frame)
            for det in dets:
                obj = ObjectDetection(
                    id=uuid.uuid4(),
                    frame_id=frame.id,
                    video_id=frame.video_id,
                    label=det["label"],
                    confidence=det["confidence"],
                    bounding_box=det["bounding_box"],
                    crop_path=frame.image_path,  # Point crop_path to the frame image so crop_url points to real image!
                    metadata_json=det.get("metadata", {})
                )
                db.add(obj)
                new_objs.append(obj)

        await db.commit()
        print(f"Saved {len(new_objs)} ObjectDetection records.")

        # Create Embeddings for Objects
        obj_vectors = await clip_service.generate_object_embeddings_batch(new_objs)
        for obj, vec in zip(new_objs, obj_vectors):
            emb = Embedding(
                id=uuid.uuid4(),
                frame_id=None,
                object_id=obj.id,
                embedding=vec,
                model_name=f"CLIP-{clip_service.model_name}",
                dimension=clip_service.dimension
            )
            db.add(emb)

        await db.commit()
        print(f"Successfully saved {len(frames) + len(new_objs)} total embeddings.")

        # Rebuild FAISS index
        print("\nRebuilding FAISS index...")
        result = await faiss_service.build_index_from_db(db)
        print("FAISS Index rebuild result:", result)

asyncio.run(populate_accurate_detections())
