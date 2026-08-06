/**
 * ByteTrack API Service
 */

import { api } from '@/lib/api'
import {
  TrackSummary,
  TrackDetail,
  VisualizationResponse,
} from '@/types/bytetrack'

export class ByteTrackService {
  /**
   * Run ByteTrack tracking on video detections
   */
  static async runTracking(videoId: string) {
    const response = await api.post<{
      video_id: string
      total_frames_processed: number
      objects_tracked: number
      distinct_track_count: number
      status: string
    }>(`/videos/${videoId}/track-objects`)
    return response.data
  }

  /**
   * List distinct object motion tracks for video
   */
  static async getTracks(videoId: string, minDetections = 1): Promise<TrackSummary[]> {
    const response = await api.get<TrackSummary[]>(`/videos/${videoId}/tracks`, {
      params: { min_detections: minDetections },
    })
    return response.data
  }

  /**
   * Get detailed trajectory timeline for a specific track ID
   */
  static async getTrackDetail(videoId: string, trackId: number): Promise<TrackDetail> {
    const response = await api.get<TrackDetail>(`/videos/${videoId}/tracks/${trackId}`)
    return response.data
  }

  /**
   * Get motion trajectory visualization payload (SVG polylines & 2D points)
   */
  static async getVisualization(
    videoId: string,
    trackId?: number
  ): Promise<VisualizationResponse> {
    const params: Record<string, any> = {}
    if (trackId !== undefined) params.track_id = trackId

    const response = await api.get<VisualizationResponse>(`/videos/${videoId}/tracks/visualization`, {
      params,
    })
    return response.data
  }
}
