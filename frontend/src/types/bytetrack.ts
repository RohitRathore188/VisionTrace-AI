/**
 * ByteTrack Types & Interfaces
 */

export interface TrackSummary {
  track_id: number
  label: string
  total_detections: number
  start_timestamp: number
  end_timestamp: number
  duration_seconds: number
  spatial_displacement: number
  start_frame_number: number
  end_frame_number: number
}

export interface TrajectoryPoint {
  object_id: string
  frame_id: string
  frame_number: number
  timestamp_seconds: number
  center: [number, number]
  bounding_box: {
    xmin: number
    ymin: number
    xmax: number
    ymax: number
  }
  confidence: number
  crop_url?: string
  frame_url?: string
}

export interface TrackDetail {
  video_id: string
  track_id: number
  label: string
  total_keyframes: number
  start_timestamp: number
  end_timestamp: number
  trajectory: TrajectoryPoint[]
}

export interface VisualizationPoint {
  x: number
  y: number
  timestamp: number
  frame_number: number
}

export interface VisualizationTrack {
  track_id: number
  label: string
  points: VisualizationPoint[]
  svg_path: string
}

export interface VisualizationResponse {
  video_id: string
  tracks: VisualizationTrack[]
}
