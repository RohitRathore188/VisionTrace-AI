/**
 * Object Detection Types & Interfaces
 */

export type TargetCategory = 'person' | 'vehicle' | 'bag' | 'phone' | 'laptop' | 'animal'

export interface BoundingBox {
  xmin: number
  ymin: number
  xmax: number
  ymax: number
}

export interface DetectedObject {
  id: string
  frameId: string
  videoId: string
  trackId?: number
  label: TargetCategory | string
  confidence: number
  boundingBox: BoundingBox
  cropPath?: string
  metadataJson: Record<string, any>
  createdAt: string
  timestampSeconds?: number
  frameNumber?: number
  cropUrl?: string
}

export interface YOLODetectionRequest {
  confidence_threshold: number
  target_classes?: string[]
}

export interface YOLODetectionProgress {
  video_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  total_frames: number
  processed_frames: number
  detected_objects_count: number
  progress_percent: number
  error_message?: string
  started_at?: string
  updated_at?: string
}

export interface ObjectListResponse {
  items: DetectedObject[]
  total: number
  page: number
  pageSize: number
  pages: number
}
