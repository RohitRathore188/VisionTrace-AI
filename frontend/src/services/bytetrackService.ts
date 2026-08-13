import { api } from '@/lib/api'
import { TrackSummary, TrackDetail, VisualizationResponse, ByteTrackRunResponse } from '@/types/bytetrack'

export interface TrajectoryPoint {
  object_id: string
  frame_id: string
  frame_number: number
  timestamp_seconds: number
  confidence: number
  bounding_box: {
    xmin: number
    ymin: number
    xmax: number
    ymax: number
  }
}

export interface TrackData {
  track_id: number
  label: string
  first_seen: number
  last_seen: number
  total_frames: number
  trajectory: TrajectoryPoint[]
}

export interface VideoTrajectoriesResponse {
  video_id: string
  total_tracks: number
  tracks: TrackData[]
}

export class ByteTrackService {
  static async runTracking(videoId: string): Promise<ByteTrackRunResponse> {
    const res = await api.post<ByteTrackRunResponse>(`/videos/${videoId}/track-objects`)
    return res.data
  }

  static async getTracks(videoId: string, minDetections = 1): Promise<TrackSummary[]> {
    const res = await api.get<TrackSummary[]>(`/videos/${videoId}/tracks`, {
      params: { min_detections: minDetections },
    })
    return res.data
  }

  static async getTrackDetail(videoId: string, trackId: number): Promise<TrackDetail> {
    const res = await api.get<TrackDetail>(`/videos/${videoId}/tracks/${trackId}`)
    return res.data
  }

  static async getVisualization(videoId: string, trackId?: number): Promise<VisualizationResponse> {
    const res = await api.get<VisualizationResponse>(`/videos/${videoId}/tracks/visualization`, {
      params: trackId ? { track_id: trackId } : {},
    })
    return res.data
  }

  static async getAllTrajectories(videoId: string): Promise<VideoTrajectoriesResponse> {
    const res = await api.get<VideoTrajectoriesResponse>(`/videos/${videoId}/all-trajectories`)
    return res.data
  }
}
