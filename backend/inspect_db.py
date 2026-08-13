import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def inspect_db():
    from app.db.session import async_session_factory
    from app.models.video import Video
    from app.models.frame import Frame
    from app.models.object import ObjectDetection
    from app.models.embedding import Embedding
    from sqlalchemy import select, func

    async with async_session_factory() as db:
        v_res = await db.execute(select(Video))
        videos = v_res.scalars().all()
        print(f"Total Videos: {len(videos)}")
        for v in videos:
            print(f"  Video ID: {v.id} | Title: {v.title} | Status: {v.status} | Path: {v.file_path}")

        f_res = await db.execute(select(Frame))
        frames = f_res.scalars().all()
        print(f"\nTotal Frames: {len(frames)}")

        o_res = await db.execute(select(ObjectDetection))
        objs = o_res.scalars().all()
        print(f"\nTotal Objects Detected: {len(objs)}")
        for obj in objs[:10]:
            print(f"  Obj ID: {obj.id} | Frame ID: {obj.frame_id} | Label: {obj.label} | Confidence: {obj.confidence}")

        e_res = await db.execute(select(Embedding))
        embs = e_res.scalars().all()
        print(f"\nTotal Embeddings: {len(embs)}")
        for e in embs[:10]:
            print(f"  Emb ID: {e.id} | Frame ID: {e.frame_id} | Object ID: {e.object_id} | Model: {e.model_name}")

asyncio.run(inspect_db())
