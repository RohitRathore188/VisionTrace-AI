import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_real_yolo():
    from app.db.session import async_session_factory
    from app.models.frame import Frame
    from app.models.object import ObjectDetection
    from app.services.yolo_service import yolo_service
    from sqlalchemy import select, delete

    async with async_session_factory() as db:
        # Get extracted keyframes
        f_res = await db.execute(select(Frame))
        frames = list(f_res.scalars().all())
        print(f"Found {len(frames)} keyframes in DB.")

        # Test yolo_service on first 5 frames
        for frame in frames[:5]:
            print(f"\nProcessing Frame ID: {frame.id} | Image Path: {frame.image_path}")
            detections = await yolo_service.detect_objects_in_frame(frame, confidence_threshold=0.25)
            print(f"  Detections count: {len(detections)}")
            for det in detections:
                print(f"    Label: {det['label']} ({det['raw_label']}) | Conf: {det['confidence']} | BBox: {det['bounding_box']}")

asyncio.run(test_real_yolo())
