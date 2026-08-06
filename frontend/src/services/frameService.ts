/**
 * Frame Extraction API Service
 */

import { api } from '@/lib/api'
import { FrameExtractionProgress, FrameListResponse } from '@/types/frame'

export class FrameService {
  /**
   * Trigger OpenCV background frame extraction
   */
  static async triggerExtraction(
    videoId: string,
    intervalSeconds = 1.0,
    jpegQuality = 85
  ): Promise<FrameExtractionProgress> {
    const response = await api.post<FrameExtractionProgress>(`/videos/${videoId}/extract-frames`, {
      interval_seconds: intervalSeconds,
      jpeg_quality: jpegQuality,
    })
    return response.data
  }

  /**
   * Poll frame extraction progress
   */
  static async getExtractionStatus(videoId: string): Promise<FrameExtractionProgress> {
    const response = await api.get<FrameExtractionProgress>(`/videos/${videoId}/extraction/status`)
    return response.data
  }

  /**
   * Get extracted keyframes list for a video
   */
  static async getExtractedFrames(
    videoId: string,
    page = 1,
    pageSize = 50
  ): Promise<FrameListResponse> {
    const response = await api.get<FrameListResponse>(`/videos/${videoId}/frames`, {
      params: { page, page_size: pageSize },
    })
    return response.data
  }
}
