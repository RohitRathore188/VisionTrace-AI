/**
 * Frame Types & Interfaces
 */

export interface FrameExtractionRequest {
  interval_seconds: number
  jpeg_quality?: number
}

export interface FrameExtractionProgress {
  video_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  total_frames: number
  processed_frames: number
  extracted_count: number
  progress_percent: number
  current_timestamp: number
  error_message?: string
  retry_count: number
  started_at?: string
  updated_at?: string
}

export interface Frame {
  id: string
  videoId: string
  frameNumber: number
  timestampSeconds: number
  imagePath: string
  width?: number
  height?: number
  metadataJson: Record<string, any>
  createdAt: string
  imageUrl?: string
}

export interface FrameListResponse {
  items: Frame[]
  total: number
  page: number
  pageSize: number
  pages: number
}
