import asyncio
import sys
import os
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_frame_paths():
    from app.db.session import async_session_factory
    from app.models.frame import Frame
    from sqlalchemy import select

    async with async_session_factory() as db:
        f_res = await db.execute(select(Frame))
        frames = list(f_res.scalars().all())
        print(f"Total frames: {len(frames)}")

        for frame in frames[:5]:
            print(f"\nFrame ID: {frame.id}")
            print(f"  Frame image_path field: '{frame.image_path}'")
            
            possible_paths = [
                frame.image_path,
                os.path.join(os.getcwd(), frame.image_path),
                os.path.join(os.getcwd(), "data", "frames", frame.image_path),
                os.path.join(os.getcwd(), "backend", "data", "frames", frame.image_path),
                os.path.join(os.getcwd(), "data", "frames", str(frame.video_id), f"frame_{frame.frame_number:06d}.jpg"),
                os.path.join(os.getcwd(), "backend", "data", "frames", str(frame.video_id), f"frame_{frame.frame_number:06d}.jpg"),
            ]
            
            found = False
            for p in possible_paths:
                if p and os.path.exists(p):
                    img = cv2.imread(p)
                    if img is not None:
                        print(f"  FOUND: '{p}' (Shape: {img.shape})")
                        found = True
                        break
            if not found:
                print(f"  NOT FOUND on disk!")

asyncio.run(test_frame_paths())
