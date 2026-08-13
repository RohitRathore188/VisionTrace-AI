import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def generate_object_embeddings():
    from app.db.session import async_session_factory
    from app.models.frame import Frame
    from app.models.object import ObjectDetection
    from app.models.embedding import Embedding
    from app.services.faiss_service import faiss_service
    from app.services.clip_service import clip_service
    from sqlalchemy import select, delete
    import uuid

    async with async_session_factory() as db:
        # Delete existing embeddings to re-index both frames and objects
        await db.execute(delete(Embedding))
        await db.commit()
        print("Cleared old embeddings from DB.")

        # Get all frames
        f_res = await db.execute(select(Frame))
        frames = list(f_res.scalars().all())
        print(f"Generating embeddings for {len(frames)} frames...")
        
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

        # Get all objects
        o_res = await db.execute(select(ObjectDetection))
        objs = list(o_res.scalars().all())
        print(f"Generating embeddings for {len(objs)} detected objects...")
        
        obj_vectors = await clip_service.generate_object_embeddings_batch(objs)
        for obj, vec in zip(objs, obj_vectors):
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
        print(f"Successfully saved {len(frames) + len(objs)} embeddings to DB.")

        # Rebuild FAISS index from DB
        print("\nRebuilding FAISS index...")
        result = await faiss_service.build_index_from_db(db)
        print("FAISS Index build result:", result)

asyncio.run(generate_object_embeddings())
