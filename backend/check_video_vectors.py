import asyncio
from app.db.session import AsyncSessionLocal
from app.services.faiss_service import faiss_service
from sqlalchemy import select
from app.models.video import Video
from app.models.frame import Frame

async def check():
    async with AsyncSessionLocal() as db:
        await faiss_service.build_index_from_db(db)
        print(f"Total FAISS index vectors: {len(faiss_service._metadata_map)}")
        
        # Print all video IDs in metadata map
        v_ids = set()
        for vid, meta in faiss_service._metadata_map.items():
            v_ids.add((meta.get("video_id"), meta.get("video_title")))
        print("Videos in FAISS index metadata:")
        for vid, title in v_ids:
            print(f" - ID: {vid} | Title: {title}")

        # Check video 3530201-hd_1280_720_30fps
        res = await db.execute(select(Video))
        videos = res.scalars().all()
        print("\nAll Videos in database:")
        for v in videos:
            print(f" - DB Video ID: {v.id} | Title: {v.title}")

if __name__ == "__main__":
    asyncio.run(check())
