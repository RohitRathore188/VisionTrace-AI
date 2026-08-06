/**
 * Video File Validation & Client Metadata Extraction
 */

import { VideoMetadata, VideoValidationResult } from '@/types/video'

export const ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv']
export const ALLOWED_MIME_TYPES = [
  'video/mp4',
  'video/x-msvideo',
  'video/quicktime',
  'video/x-matroska',
  'video/webm',
]
export const MAX_VIDEO_SIZE_MB = 2048 // 2 GB

/**
 * Format bytes into human readable string (KB, MB, GB)
 */
export function formatBytes(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}

/**
 * Format duration seconds to MM:SS or HH:MM:SS
 */
export function formatDuration(seconds?: number): string {
  if (!seconds || seconds <= 0) return '00:00'
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  if (hrs > 0) {
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

/**
 * Extract technical metadata from HTML5 Video element
 */
export function extractVideoMetadata(file: File): Promise<VideoMetadata> {
  return new Promise((resolve) => {
    const video = document.createElement('video')
    video.preload = 'metadata'

    const objectUrl = URL.createObjectURL(file)

    video.onloadedmetadata = () => {
      URL.revokeObjectURL(objectUrl)
      const durationSeconds = video.duration || 0
      const width = video.videoWidth || 0
      const height = video.videoHeight || 0
      const aspectRatio = width && height ? `${width}:${height}` : undefined

      resolve({
        durationSeconds: Math.round(durationSeconds * 100) / 100,
        width,
        height,
        fps: 30, // Default estimate
        fileSizeBytes: file.size,
        mimeType: file.type || 'video/mp4',
        aspectRatio,
      })
    }

    video.onerror = () => {
      URL.revokeObjectURL(objectUrl)
      resolve({
        fileSizeBytes: file.size,
        mimeType: file.type || 'video/mp4',
      })
    }

    video.src = objectUrl
  })
}

/**
 * Validate video file against format and size restrictions
 */
export async function validateVideoFile(file: File): Promise<VideoValidationResult> {
  if (!file) {
    return { isValid: false, error: 'No file provided' }
  }

  // Check file size
  const maxBytes = MAX_VIDEO_SIZE_MB * 1024 * 1024
  if (file.size > maxBytes) {
    return {
      isValid: false,
      error: `File size exceeds the ${MAX_VIDEO_SIZE_MB}MB limit (${formatBytes(file.size)})`,
    }
  }

  // Check extension
  const fileName = file.name.toLowerCase()
  const hasValidExt = ALLOWED_VIDEO_EXTENSIONS.some((ext) => fileName.endsWith(ext))
  const hasValidMime = ALLOWED_MIME_TYPES.some((mime) => file.type.toLowerCase().includes(mime.split('/')[1]))

  if (!hasValidExt && !hasValidMime) {
    return {
      isValid: false,
      error: `Unsupported file format. Supported formats: ${ALLOWED_VIDEO_EXTENSIONS.join(', ')}`,
    }
  }

  // Extract metadata
  const metadata = await extractVideoMetadata(file)

  return {
    isValid: true,
    metadata,
  }
}
