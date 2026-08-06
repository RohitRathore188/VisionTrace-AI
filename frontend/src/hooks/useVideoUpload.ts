/**
 * Custom Hook: useVideoUpload
 * Manages Drag & Drop, File Validation, Video Preview, Chunked Resumable Uploads, and Progress Tracking
 */

import { useState, useRef, useCallback, useEffect } from 'react'
import { VideoMetadata, UploadProgressState, Video } from '@/types/video'
import { validateVideoFile } from '@/lib/videoValidation'
import { VideoService } from '@/services/videoService'

const CHUNK_SIZE = 5 * 1024 * 1024 // 5MB chunks for resumable upload

export function useVideoUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [metadata, setMetadata] = useState<VideoMetadata | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)
  const [isValidating, setIsValidating] = useState<boolean>(false)

  // Upload metadata form state
  const [title, setTitle] = useState<string>('')
  const [description, setDescription] = useState<string>('')

  // Progress state
  const [progress, setProgress] = useState<UploadProgressState>({
    bytesUploaded: 0,
    totalBytes: 0,
    percentage: 0,
    speedMbps: 0,
    etaSeconds: 0,
    isPaused: false,
    isUploading: false,
    isCompleted: false,
  })

  const [uploadedVideo, setUploadedVideo] = useState<Video | null>(null)

  // Resumable Upload Refs
  const isPausedRef = useRef<boolean>(false)
  const isCancelledRef = useRef<boolean>(false)
  const startTimeRef = useRef<number>(0)
  const activeVideoIdRef = useRef<string | null>(null)

  /**
   * Handle file selection and video preview generation
   */
  const handleSelectFile = useCallback(async (selectedFile: File) => {
    setIsValidating(true)
    setValidationError(null)
    setUploadedVideo(null)

    // Reset progress
    setProgress({
      bytesUploaded: 0,
      totalBytes: selectedFile.size,
      percentage: 0,
      speedMbps: 0,
      etaSeconds: 0,
      isPaused: false,
      isUploading: false,
      isCompleted: false,
    })

    // Clean up previous preview URL
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }

    const validation = await validateVideoFile(selectedFile)
    setIsValidating(false)

    if (!validation.isValid) {
      setValidationError(validation.error || 'Invalid video file')
      setFile(null)
      setMetadata(null)
      setPreviewUrl(null)
      return false
    }

    setFile(selectedFile)
    setMetadata(validation.metadata || null)
    setTitle(selectedFile.name.replace(/\.[^/.]+$/, ''))

    // Generate local preview URL
    const url = URL.createObjectURL(selectedFile)
    setPreviewUrl(url)
    return true
  }, [previewUrl])

  /**
   * Clear file selection
   */
  const resetUpload = useCallback(() => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }
    setFile(null)
    setPreviewUrl(null)
    setMetadata(null)
    setValidationError(null)
    setTitle('')
    setDescription('')
    setUploadedVideo(null)
    isPausedRef.current = false
    isCancelledRef.current = false
    activeVideoIdRef.current = null
    setProgress({
      bytesUploaded: 0,
      totalBytes: 0,
      percentage: 0,
      speedMbps: 0,
      etaSeconds: 0,
      isPaused: false,
      isUploading: false,
      isCompleted: false,
    })
  }, [previewUrl])

  /**
   * Start Resumable Chunked Upload
   */
  const startUpload = useCallback(async () => {
    if (!file || !metadata) {
      setValidationError('No valid file selected')
      return
    }

    isPausedRef.current = false
    isCancelledRef.current = false
    startTimeRef.current = Date.now()

    setProgress((prev) => ({
      ...prev,
      isUploading: true,
      isPaused: false,
      error: undefined,
    }))

    try {
      // 1. Initialize Upload Session on Backend
      const initRes = await VideoService.initUpload({
        title: title || file.name,
        description: description,
        filename: file.name,
        file_size_bytes: file.size,
        mime_type: metadata.mimeType,
        duration_seconds: metadata.durationSeconds,
        fps: metadata.fps,
        width: metadata.width,
        height: metadata.height,
      })

      const videoId = initRes.video_id
      activeVideoIdRef.current = videoId

      // 2. Perform Resumable Chunked Upload
      const totalBytes = file.size
      const totalChunks = Math.ceil(totalBytes / CHUNK_SIZE)
      let currentBytesUploaded = 0

      for (let i = 0; i < totalChunks; i++) {
        // Handle cancellation
        if (isCancelledRef.current) {
          setProgress((prev) => ({ ...prev, isUploading: false, isCompleted: false }))
          return
        }

        // Handle pause loop
        while (isPausedRef.current) {
          await new Promise((r) => setTimeout(r, 400))
          if (isCancelledRef.current) return
        }

        const start = i * CHUNK_SIZE
        const end = Math.min(start + CHUNK_SIZE, totalBytes)
        const chunk = file.slice(start, end)

        // Upload chunk
        await VideoService.uploadChunk(videoId, i, totalChunks, chunk)

        currentBytesUploaded += chunk.size
        const elapsedTime = (Date.now() - startTimeRef.current) / 1000
        const speedBytesPerSec = elapsedTime > 0 ? currentBytesUploaded / elapsedTime : 0
        const speedMbps = Math.round((speedBytesPerSec / (1024 * 1024)) * 100) / 100
        const remainingBytes = totalBytes - currentBytesUploaded
        const etaSeconds = speedBytesPerSec > 0 ? Math.round(remainingBytes / speedBytesPerSec) : 0
        const percentage = Math.min(100, Math.round((currentBytesUploaded / totalBytes) * 100))

        setProgress({
          bytesUploaded: currentBytesUploaded,
          totalBytes,
          percentage,
          speedMbps,
          etaSeconds,
          isPaused: false,
          isUploading: true,
          isCompleted: false,
        })
      }

      // 3. Complete Upload Session
      const completedVideo = await VideoService.completeUpload(videoId, {
        file_path: initRes.storage_path,
        file_size_bytes: file.size,
        mime_type: metadata.mimeType,
        duration_seconds: metadata.durationSeconds,
        fps: metadata.fps,
        width: metadata.width,
        height: metadata.height,
      })

      setUploadedVideo(completedVideo)
      setProgress({
        bytesUploaded: totalBytes,
        totalBytes,
        percentage: 100,
        speedMbps: 0,
        etaSeconds: 0,
        isPaused: false,
        isUploading: false,
        isCompleted: true,
      })
    } catch (err: any) {
      console.error('Upload failed:', err)
      const errorMsg = err?.message || 'Upload failed. Please try again.'
      setProgress((prev) => ({
        ...prev,
        isUploading: false,
        error: errorMsg,
      }))
    }
  }, [file, metadata, title, description])

  /**
   * Pause Upload
   */
  const pauseUpload = useCallback(() => {
    isPausedRef.current = true
    setProgress((prev) => ({ ...prev, isPaused: true }))
  }, [])

  /**
   * Resume Upload
   */
  const resumeUpload = useCallback(() => {
    isPausedRef.current = false
    startTimeRef.current = Date.now()
    setProgress((prev) => ({ ...prev, isPaused: false }))
  }, [])

  /**
   * Cancel Upload
   */
  const cancelUpload = useCallback(() => {
    isCancelledRef.current = true
    isPausedRef.current = false
    resetUpload()
  }, [resetUpload])

  // Cleanup object URLs on unmount
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  return {
    file,
    previewUrl,
    metadata,
    validationError,
    isValidating,
    title,
    setTitle,
    description,
    setDescription,
    progress,
    uploadedVideo,
    handleSelectFile,
    resetUpload,
    startUpload,
    pauseUpload,
    resumeUpload,
    cancelUpload,
  }
}
