import os
import cv2
import asyncio
import uuid
from app.db.session import async_session_factory
from app.models.video import Video, VideoStatus

async def main():
    async with async_session_factory() as db:
        vid_id = uuid.UUID("029841e0-53b6-4748-8114-6c7b74ce5c9e")
        v = await db.get(Video, vid_id)
        if v:
            video_src = r"d:\Projects\VisionTrace AI\data\videos\11111111-1111-1111-1111-111111111111\029841e0-53b6-4748-8114-6c7b74ce5c9e\video_029841e0-53b6-4748-8114-6c7b74ce5c9e.mp4"
            cap = cv2.VideoCapture(video_src)
            cap.set(cv2.CAP_PROP_POS_FRAMES, 60)
            ret, frame = cap.read()
            if ret:
                frame_dir = os.path.join(os.getcwd(), "data", "frames", str(v.id))
                os.makedirs(frame_dir, exist_ok=True)
                thumb_path = os.path.join(frame_dir, "thumbnail.jpg")
                cv2.imwrite(thumb_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                print("Extracted thumbnail photo to:", thumb_path)
                
                v.metadata_json = {"thumbnail_url": f"http://localhost:8000/data/frames/{v.id}/thumbnail.jpg"}
                v.status = VideoStatus.COMPLETED
                v.error_message = None
                await db.commit()
                print("Updated Video DB record status to COMPLETED!")

if __name__ == "__main__":
    asyncio.run(main())
