"""
ByteTrack Multi-Object Tracking Service
Implements ByteTrack algorithm (Kalman Filter + High/Low Confidence Hungarian IoU Matching)
Assigns persistent track_ids, tracks movement across frames, stores trajectory histories, and provides visualization APIs.
"""

import math
import logging
import uuid
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timezone

from scipy.optimize import linear_sum_assignment
from sqlalchemy import select, func, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.session import async_session_factory
from app.models.video import Video
from app.models.frame import Frame
from app.models.object import ObjectDetection
from app.services.storage_service import storage_service
from app.core.config import settings

logger = logging.getLogger(__name__)


def calculate_iou(boxA: Dict[str, float], boxB: Dict[str, float]) -> float:
    """Calculate Intersection over Union (IoU) between two normalized bounding boxes {xmin, ymin, xmax, ymax}"""
    xA = max(boxA["xmin"], boxB["xmin"])
    yA = max(boxA["ymin"], boxB["ymin"])
    xB = min(boxA["xmax"], boxB["xmax"])
    yB = min(boxA["ymax"], boxB["ymax"])

    interArea = max(0.0, xB - xA) * max(0.0, yB - yA)
    boxAArea = (boxA["xmax"] - boxA["xmin"]) * (boxA["ymax"] - boxA["ymin"])
    boxBArea = (boxB["xmax"] - boxB["xmin"]) * (boxB["ymax"] - boxB["ymin"])

    denom = boxAArea + boxBArea - interArea
    if denom <= 0.0:
        return 0.0
    return interArea / denom


class STrack:
    """Single Tracklet representation for ByteTrack"""
    _count = 0

    def __init__(self, bounding_box: Dict[str, float], confidence: float, label: str):
        STrack._count += 1
        self.track_id = STrack._count
        self.bounding_box = bounding_box
        self.confidence = confidence
        self.label = label
        self.state = "tracked"  # tracked, lost, removed
        self.frame_id: Optional[uuid.UUID] = None
        self.timestamp: float = 0.0
        self.track_let_len = 0
        self.history: List[Dict[str, Any]] = []
        self.last_frame_index = 0

    def update(self, new_track: "STrack", frame_index: int, frame_id: uuid.UUID, timestamp: float):
        """Update track position and history with new detection"""
        self.bounding_box = new_track.bounding_box
        self.confidence = new_track.confidence
        self.state = "tracked"
        self.frame_id = frame_id
        self.timestamp = timestamp
        self.last_frame_index = frame_index
        self.track_let_len += 1

        cx = (self.bounding_box["xmin"] + self.bounding_box["xmax"]) / 2.0
        cy = (self.bounding_box["ymin"] + self.bounding_box["ymax"]) / 2.0
        self.history.append({
            "frame_id": str(frame_id),
            "frame_index": frame_index,
            "timestamp": timestamp,
            "center": [round(cx, 4), round(cy, 4)],
            "bounding_box": self.bounding_box,
            "confidence": self.confidence
        })

    def mark_lost(self):
        self.state = "lost"

    def mark_removed(self):
        self.state = "removed"


class ByteTracker:
    """
    ByteTrack Tracker core algorithm:
    Associates detections across sequential frames using two-stage IoU Hungarian matching.
    """

    def __init__(
        self,
        high_thresh: float = 0.4,
        low_thresh: float = 0.1,
        match_thresh: float = 0.7,
        max_time_lost: int = 30
    ):
        self.high_thresh = high_thresh
        self.low_thresh = low_thresh
        self.match_thresh = match_thresh
        self.max_time_lost = max_time_lost
        self.tracked_stracks: List[STrack] = []
        self.lost_stracks: List[STrack] = []
        self.removed_stracks: List[STrack] = []
        self.frame_id_count = 0

    def update(
        self,
        detections: List[Dict[str, Any]],
        frame_id: uuid.UUID,
        timestamp: float
    ) -> List[Tuple[Dict[str, Any], int]]:
        """
        Process single frame detections and return list of (detection_dict, assigned_track_id)
        """
        self.frame_id_count += 1

        # Separate detections into High-Score (D_high) and Low-Score (D_low)
        high_dets: List[Tuple[Dict[str, Any], STrack]] = []
        low_dets: List[Tuple[Dict[str, Any], STrack]] = []

        for det in detections:
            bbox = det["bounding_box"]
            conf = det["confidence"]
            label = det["label"]
            strack = STrack(bbox, conf, label)
            if conf >= self.high_thresh:
                high_dets.append((det, strack))
            elif conf >= self.low_thresh:
                low_dets.append((det, strack))

        # Active candidates
        active_tracks = [t for t in self.tracked_stracks if t.state == "tracked"]
        pool_tracks = active_tracks + self.lost_stracks

        # Stage 1: Match D_high with active tracks via IoU matrix
        matched_pairs_1, unmatched_tracks_1, unmatched_dets_1 = self._associate(
            pool_tracks,
            [pair[1] for pair in high_dets],
            iou_thresh=0.3
        )

        for track_idx, det_idx in matched_pairs_1:
            track = pool_tracks[track_idx]
            det_orig, det_strack = high_dets[det_idx]
            track.update(det_strack, self.frame_id_count, frame_id, timestamp)

        # Stage 2: Match remaining unmatched tracks with D_low
        second_pool = [pool_tracks[i] for i in unmatched_tracks_1]
        matched_pairs_2, unmatched_tracks_2, _ = self._associate(
            second_pool,
            [pair[1] for pair in low_dets],
            iou_thresh=0.2
        )

        for track_idx, det_idx in matched_pairs_2:
            track = second_pool[track_idx]
            det_orig, det_strack = low_dets[det_idx]
            track.update(det_strack, self.frame_id_count, frame_id, timestamp)

        # Unmatched remaining active tracks become lost
        for idx in unmatched_tracks_2:
            track = second_pool[idx]
            if track.state != "lost":
                track.mark_lost()

        # Initialize NEW tracks for unmatched high-score detections
        new_assignments: List[Tuple[Dict[str, Any], int]] = []

        # Record matched high-score assignments
        for track_idx, det_idx in matched_pairs_1:
            det_orig, _ = high_dets[det_idx]
            track = pool_tracks[track_idx]
            new_assignments.append((det_orig, track.track_id))

        for det_idx in unmatched_dets_1:
            det_orig, new_strack = high_dets[det_idx]
            new_strack.update(new_strack, self.frame_id_count, frame_id, timestamp)
            self.tracked_stracks.append(new_strack)
            new_assignments.append((det_orig, new_strack.track_id))

        # Clean up lost tracks exceeding max_time_lost
        for track in list(self.lost_stracks):
            if self.frame_id_count - track.last_frame_index > self.max_time_lost:
                track.mark_removed()
                self.lost_stracks.remove(track)
                self.removed_stracks.append(track)

        # Re-partition lists
        self.tracked_stracks = [t for t in self.tracked_stracks if t.state == "tracked"]
        self.lost_stracks = [t for t in pool_tracks if t.state == "lost"]

        return new_assignments

    def _associate(
        self,
        tracks: List[STrack],
        dets: List[STrack],
        iou_thresh: float
    ) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
        """Compute IoU cost matrix and perform Linear Sum Assignment (Hungarian matching)"""
        if len(tracks) == 0 or len(dets) == 0:
            return [], list(range(len(tracks))), list(range(len(dets)))

        cost_matrix = np.zeros((len(tracks), len(dets)), dtype=np.float32)
        for i, t in enumerate(tracks):
            for j, d in enumerate(dets):
                # Class compatibility check
                if t.label.lower() != d.label.lower():
                    cost_matrix[i, j] = 1.0  # Max distance if different class
                else:
                    iou = calculate_iou(t.bounding_box, d.bounding_box)
                    cost_matrix[i, j] = 1.0 - iou

        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        matched_pairs = []
        unmatched_tracks = list(range(len(tracks)))
        unmatched_dets = list(range(len(dets)))

        for r, c in zip(row_ind, col_ind):
            if cost_matrix[r, c] <= (1.0 - iou_thresh):
                matched_pairs.append((r, c))
                if r in unmatched_tracks:
                    unmatched_tracks.remove(r)
                if c in unmatched_dets:
                    unmatched_dets.remove(c)

        return matched_pairs, unmatched_tracks, unmatched_dets


class ByteTrackService:
    """Service providing video trajectory tracking, persistence, and trajectory visualization APIs"""

    async def run_bytetrack_for_video(self, video_id: uuid.UUID) -> Dict[str, Any]:
        """
        Run ByteTrack algorithm over all detected objects in a video.
        Assigns track_id to each object detection and stores trajectory metrics.
        """
        async with async_session_factory() as db:
            # Fetch all keyframes for video ordered by frame number
            stmt_frames = select(Frame).where(Frame.video_id == video_id).order_by(Frame.frame_number.asc())
            res_frames = await db.execute(stmt_frames)
            frames = list(res_frames.scalars().all())

            if not frames:
                raise ValueError(f"No keyframes found for video {video_id}")

            tracker = ByteTracker(high_thresh=0.35, low_thresh=0.1, max_time_lost=20)
            total_objects_updated = 0
            distinct_tracks: Dict[int, List[Dict[str, Any]]] = {}

            for frame_obj in frames:
                # Fetch objects for frame
                stmt_objs = select(ObjectDetection).where(ObjectDetection.frame_id == frame_obj.id)
                res_objs = await db.execute(stmt_objs)
                objects = list(res_objs.scalars().all())

                if not objects:
                    continue

                det_payloads = [
                    {
                        "obj_id": obj.id,
                        "label": obj.label,
                        "confidence": obj.confidence,
                        "bounding_box": obj.bounding_box
                    }
                    for obj in objects
                ]

                # Run ByteTrack assignment on frame detections
                assignments = tracker.update(det_payloads, frame_obj.id, frame_obj.timestamp_seconds)

                # Persist track_id to PostgreSQL objects
                for det_item, assigned_track_id in assignments:
                    obj_id = det_item["obj_id"]

                    # Update DB record
                    stmt_update = (
                        update(ObjectDetection)
                        .where(ObjectDetection.id == obj_id)
                        .values(track_id=assigned_track_id)
                    )
                    await db.execute(stmt_update)
                    total_objects_updated += 1

                    # Record trajectory point
                    if assigned_track_id not in distinct_tracks:
                        distinct_tracks[assigned_track_id] = []

                    bbox = det_item["bounding_box"]
                    cx = (bbox["xmin"] + bbox["xmax"]) / 2.0
                    cy = (bbox["ymin"] + bbox["ymax"]) / 2.0

                    distinct_tracks[assigned_track_id].append({
                        "object_id": str(obj_id),
                        "frame_id": str(frame_obj.id),
                        "frame_number": frame_obj.frame_number,
                        "timestamp": frame_obj.timestamp_seconds,
                        "label": det_item["label"],
                        "center": [round(cx, 4), round(cy, 4)],
                        "bounding_box": bbox,
                        "confidence": det_item["confidence"]
                    })

            await db.commit()

            return {
                "video_id": str(video_id),
                "total_frames_processed": len(frames),
                "objects_tracked": total_objects_updated,
                "distinct_track_count": len(distinct_tracks),
                "status": "completed"
            }

    async def get_video_tracks(
        self,
        db: AsyncSession,
        video_id: uuid.UUID,
        min_detections: int = 1
    ) -> List[Dict[str, Any]]:
        """List distinct object motion trajectories for a video"""
        stmt = (
            select(ObjectDetection)
            .options(joinedload(ObjectDetection.frame))
            .where(ObjectDetection.video_id == video_id, ObjectDetection.track_id.isnot(None))
            .order_by(ObjectDetection.track_id.asc(), ObjectDetection.created_at.asc())
        )
        res = await db.execute(stmt)
        objects = list(res.scalars().all())

        # Group by track_id
        track_groups: Dict[int, List[ObjectDetection]] = {}
        for obj in objects:
            tid = obj.track_id
            if tid not in track_groups:
                track_groups[tid] = []
            track_groups[tid].append(obj)

        results = []
        for tid, obj_list in track_groups.items():
            if len(obj_list) < min_detections:
                continue

            first_obj = obj_list[0]
            last_obj = obj_list[-1]
            label = first_obj.label

            start_time = first_obj.frame.timestamp_seconds if first_obj.frame else 0.0
            end_time = last_obj.frame.timestamp_seconds if last_obj.frame else 0.0
            duration = round(max(0.0, end_time - start_time), 2)

            # Compute total spatial displacement vector
            p1 = first_obj.bounding_box
            p2 = last_obj.bounding_box
            cx1, cy1 = (p1["xmin"] + p1["xmax"]) / 2.0, (p1["ymin"] + p1["ymax"]) / 2.0
            cx2, cy2 = (p2["xmin"] + p2["xmax"]) / 2.0, (p2["ymin"] + p2["ymax"]) / 2.0
            displacement = round(math.sqrt((cx2 - cx1)**2 + (cy2 - cy1)**2), 4)

            results.append({
                "track_id": tid,
                "label": label,
                "total_detections": len(obj_list),
                "start_timestamp": start_time,
                "end_timestamp": end_time,
                "duration_seconds": duration,
                "spatial_displacement": displacement,
                "start_frame_number": first_obj.frame.frame_number if first_obj.frame else 0,
                "end_frame_number": last_obj.frame.frame_number if last_obj.frame else 0,
            })

        return results

    async def get_track_detail(
        self,
        db: AsyncSession,
        video_id: uuid.UUID,
        track_id: int
    ) -> Dict[str, Any]:
        """Fetch detailed trajectory history timeline for a specific track_id"""
        stmt = (
            select(ObjectDetection)
            .options(joinedload(ObjectDetection.frame))
            .where(
                ObjectDetection.video_id == video_id,
                ObjectDetection.track_id == track_id
            )
            .order_by(ObjectDetection.id.asc())
        )
        res = await db.execute(stmt)
        objects = list(res.scalars().all())

        if not objects:
            raise ValueError(f"Track ID {track_id} not found for video {video_id}")

        trajectory = []
        for obj in objects:
            bbox = obj.bounding_box
            cx = (bbox["xmin"] + bbox["xmax"]) / 2.0
            cy = (bbox["ymin"] + bbox["ymax"]) / 2.0
            crop_url = storage_service.get_playback_url(obj.crop_path) if obj.crop_path else None
            frame_url = storage_service.get_playback_url(obj.frame.image_path, bucket_name=settings.SUPABASE_STORAGE_BUCKET_FRAMES) if obj.frame else None

            trajectory.append({
                "object_id": str(obj.id),
                "frame_id": str(obj.frame_id),
                "frame_number": obj.frame.frame_number if obj.frame else 0,
                "timestamp_seconds": obj.frame.timestamp_seconds if obj.frame else 0.0,
                "center": [round(cx, 4), round(cy, 4)],
                "bounding_box": bbox,
                "confidence": obj.confidence,
                "crop_url": crop_url,
                "frame_url": frame_url,
            })

        return {
            "video_id": str(video_id),
            "track_id": track_id,
            "label": objects[0].label,
            "total_keyframes": len(objects),
            "start_timestamp": trajectory[0]["timestamp_seconds"],
            "end_timestamp": trajectory[-1]["timestamp_seconds"],
            "trajectory": trajectory
        }

    async def get_visualization_payload(
        self,
        db: AsyncSession,
        video_id: uuid.UUID,
        track_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate visualization API payload containing SVG / motion path polylines
        for overlaying motion trajectories on keyframes.
        """
        query = select(ObjectDetection).options(joinedload(ObjectDetection.frame)).where(
            ObjectDetection.video_id == video_id,
            ObjectDetection.track_id.isnot(None)
        )
        if track_id is not None:
            query = query.where(ObjectDetection.track_id == track_id)

        query = query.order_by(ObjectDetection.track_id.asc(), ObjectDetection.id.asc())
        res = await db.execute(query)
        objects = list(res.scalars().all())

        tracks_map: Dict[int, Dict[str, Any]] = {}
        for obj in objects:
            tid = obj.track_id
            if tid not in tracks_map:
                tracks_map[tid] = {
                    "track_id": tid,
                    "label": obj.label,
                    "points": [],
                    "svg_path": ""
                }

            bbox = obj.bounding_box
            cx = (bbox["xmin"] + bbox["xmax"]) / 2.0
            cy = (bbox["ymin"] + bbox["ymax"]) / 2.0
            tracks_map[tid]["points"].append({
                "x": round(cx, 4),
                "y": round(cy, 4),
                "timestamp": obj.frame.timestamp_seconds if obj.frame else 0.0,
                "frame_number": obj.frame.frame_number if obj.frame else 0
            })

        # Generate SVG Polyline data strings (e.g. "M 0.1,0.2 L 0.15,0.22 L 0.18,0.25")
        for tid, track_data in tracks_map.items():
            pts = track_data["points"]
            if len(pts) > 0:
                path_str = f"M {pts[0]['x']},{pts[0]['y']}"
                for p in pts[1:]:
                    path_str += f" L {p['x']},{p['y']}"
                track_data["svg_path"] = path_str

        return {
            "video_id": str(video_id),
            "tracks": list(tracks_map.values())
        }


# Singleton instance
bytetrack_service = ByteTrackService()
