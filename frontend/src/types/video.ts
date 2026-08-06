/**
 * Video Types & Interfaces
 */

export type VideoStatus = 'pending' | 'uploading' | 'processing' | 'completed' | 'failed'

export interface VideoMetadata {
  durationSeconds?: number
  fps?: number
  width?: number
  height?: number
  fileSizeBytes: number
  mimeType: string
  aspectRatio?: string
}

export interface Video {
  id: string
  userId: string
  title: string
  description?: string
  filePath: string
  fileSizeBytes?: number
  mimeType: string
  durationSeconds?: number
  fps?: number
  width?: number
  height?: number
  totalFrames?: number
  status: VideoStatus
  errorMessage?: string
  metadataJson: Record<string, any>
  createdAt: string
  updatedAt: string
  playbackUrl?: string
}

export interface VideoUploadInitRequest {
  title: string
  description?: string
  filename: string
  file_size_bytes: number
  mime_type: string
  duration_seconds?: number
  fps?: number
  width?: number
  height?: number
  metadata_json?: Record<string, any>
}

export interface VideoUploadInitResponse {
  video_id: string
  upload_url?: string
  storage_path: string
  bucket_name: string
  chunk_size: number
  resumable: boolean
}

export interface VideoUploadCompleteRequest {
  file_path: string
  file_size_bytes: number
  mime_type?: string
  duration_seconds?: number
  fps?: number
  width?: number
  height?: number
  total_frames?: number
  metadata_json?: Record<string, any>
}

export interface VideoValidationResult {
  isValid: boolean
  error?: string
  metadata?: VideoMetadata
}

export interface UploadProgressState {
  bytesUploaded: number
  totalBytes: number
  percentage: number
  speedMbps: number
  etaSeconds: number
  isPaused: boolean
  isUploading: boolean
  isCompleted: boolean
  error?: string
}
