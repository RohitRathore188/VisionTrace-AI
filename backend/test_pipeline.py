import asyncio
from sqlalchemy import select
from app.db.session import async_session_factory
from app.models.video import Video
from app.services.frame_extractor import frame_extraction_service

async def main():
    async with async_session_factory() as db:
        res = await db.execute(select(Video))
        videos = list(res.scalars().all())
        print(f"Found {len(videos)} video records in database")
        for v in videos:
            print(f"--- Processing Video ID: {v.id} | Title: {v.title} ---")
            await frame_extraction_service._process_video_extraction(v.id, interval_seconds=1.0)
            await db.refresh(v)
            print(f"    Status: {v.status.value} | Total Frames: {v.total_frames} | Error: {v.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
