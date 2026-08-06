/**
 * Video API Service
 * Handles communications with Backend Video APIs and Supabase Storage uploads
 */

import { api } from '@/lib/api'
import { supabase } from '@/lib/supabase'
import {
  Video,
  VideoUploadInitRequest,
  VideoUploadInitResponse,
  VideoUploadCompleteRequest,
  VideoStatus,
} from '@/types/video'

export class VideoService {
  /**
   * Initialize video upload session
   */
  static async initUpload(payload: VideoUploadInitRequest): Promise<VideoUploadInitResponse> {
    const response = await api.post<VideoUploadInitResponse>('/videos/upload/init', payload)
    return response.data
  }

  /**
   * Finalize video upload session
   */
  static async completeUpload(
    videoId: string,
    payload: VideoUploadCompleteRequest
  ): Promise<Video> {
    const response = await api.post<Video>(`/videos/${videoId}/complete`, payload)
    return response.data
  }

  /**
   * Upload single chunk to backend (fallback mechanism)
   */
  static async uploadChunk(
    videoId: string,
    chunkIndex: number,
    totalChunks: number,
    chunk: Blob,
    onProgress?: (progress: number) => void
  ) {
    const formData = new FormData()
    formData.append('video_id', videoId)
    formData.append('chunk_index', chunkIndex.toString())
    formData.append('total_chunks', totalChunks.toString())
    formData.append('chunk_file', chunk, `chunk_${chunkIndex}`)

    const response = await api.post('/videos/upload/chunk', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (event) => {
        if (event.total && onProgress) {
          onProgress(event.loaded / event.total)
        }
      },
    })
    return response.data
  }

  /**
   * Direct upload file to Supabase Storage bucket
   */
  static async uploadToSupabaseDirect(
    bucketName: string,
    storagePath: string,
    file: File,
    _onProgress?: (percent: number) => void
  ) {
    try {
      const { data, error } = await supabase.storage
        .from(bucketName)
        .upload(storagePath, file, {
          cacheControl: '3600',
          upsert: true,
        })

      if (error) {
        throw error
      }
      return data
    } catch (err: any) {
      console.warn('Supabase direct upload failed, using chunked upload fallback:', err?.message)
      throw err
    }
  }

  /**
   * List videos for logged-in user
   */
  static async getVideos(page = 1, pageSize = 20, status?: VideoStatus) {
    const params: Record<string, any> = { page, page_size: pageSize }
    if (status) params.status = status
    const response = await api.get<{ items: Video[]; total: number; pages: number }>('/videos', {
      params,
    })
    return response.data
  }

  /**
   * Poll video processing status
   */
  static async getVideoStatus(videoId: string) {
    const response = await api.get<{ video_id: string; status: VideoStatus; progress_percent: number }>(
      `/videos/${videoId}/status`
    )
    return response.data
  }

  /**
   * Delete video record and storage file
   */
  static async deleteVideo(videoId: string) {
    await api.delete(`/videos/${videoId}`)
  }
}
