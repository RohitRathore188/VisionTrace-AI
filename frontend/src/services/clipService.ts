/**
 * OpenCLIP API Service
 */

import { api } from '@/lib/api'
import {
  CLIPEmbeddingProgress,
  TextEmbeddingResponse,
} from '@/types/embedding'

export class CLIPService {
  /**
   * Trigger OpenCLIP embedding generation for video keyframes and detected objects
   */
  static async triggerEmbeddingGeneration(
    videoId: string,
    includeFrames = true,
    includeObjects = true
  ): Promise<CLIPEmbeddingProgress> {
    const response = await api.post<CLIPEmbeddingProgress>(
      `/embeddings/videos/${videoId}/generate-embeddings`,
      {
        include_frames: includeFrames,
        include_objects: includeObjects,
      }
    )
    return response.data
  }

  /**
   * Poll OpenCLIP embedding generation status
   */
  static async getEmbeddingStatus(videoId: string): Promise<CLIPEmbeddingProgress> {
    const response = await api.get<CLIPEmbeddingProgress>(`/embeddings/videos/${videoId}/embeddings/status`)
    return response.data
  }

  /**
   * Generate 512D OpenCLIP text embedding for natural language search query
   */
  static async generateTextEmbedding(queryText: string): Promise<TextEmbeddingResponse> {
    const response = await api.post<TextEmbeddingResponse>('/embeddings/text', {
      query_text: queryText,
    })
    return response.data
  }
}
