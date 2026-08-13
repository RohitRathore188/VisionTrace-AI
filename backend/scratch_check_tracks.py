import asyncio
from app.db.session import async_session_factory
from sqlalchemy import select, func
from app.models.object import ObjectDetection
from app.models.video import Video
from app.services.bytetrack_service import bytetrack_service

async def check_and_assign_tracks():
    async with async_session_factory() as db:
        res = await db.execute(select(func.count(ObjectDetection.id), func.count(ObjectDetection.track_id)))
        total_objs, tracked_objs = res.first()
        print(f"Total Objects in DB: {total_objs} | Tracked Objects: {tracked_objs}")

        # If any video has untracked objects, run ByteTrack for all videos
        video_res = await db.execute(select(Video))
        videos = list(video_res.scalars().all())

        for vid in videos:
            print(f"Running ByteTrack for Video: {vid.title} ({vid.id})...")
            try:
                res = await bytetrack_service.run_bytetrack_for_video(vid.id)
                print(f"  -> Processed {res['objects_updated']} objects into {res['distinct_track_count']} distinct tracks!")
            except Exception as e:
                print(f"  -> Error running ByteTrack: {e}")

        # Re-check count
        res_after = await db.execute(select(func.count(ObjectDetection.id), func.count(ObjectDetection.track_id)))
        total_after, tracked_after = res_after.first()
        print(f"AFTER BYTETRACK: Total Objects: {total_after} | Tracked Objects: {tracked_after}")

if __name__ == "__main__":
    asyncio.run(check_and_assign_tracks())
