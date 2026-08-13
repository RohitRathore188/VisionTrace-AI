import asyncio
import os
from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.models.video import Video
from app.models.frame import Frame

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Video))
        videos = res.scalars().all()
        print("VIDEO DISK & DB AUDIT:")
        for v in videos:
            f_res = await db.execute(select(Frame).where(Frame.video_id == v.id))
            frames = f_res.scalars().all()
            exists = os.path.exists(v.file_path) if v.file_path else False
            print(f"Video ID: {v.id}")
            print(f"  Title      : '{v.title}'")
            print(f"  File Path  : {v.file_path} (Exists on disk: {exists})")
            print(f"  Frame Count: {len(frames)} frames in DB")
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
