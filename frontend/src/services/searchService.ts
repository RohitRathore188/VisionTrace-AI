/**
 * FAISS Vector Search API Service
 */

import { api } from '@/lib/api'
import { TextSearchRequest, SearchResponse } from '@/types/search'

export class SearchService {
  /**
   * Execute natural language text-to-video visual similarity search
   */
  static async searchByText(
    queryText: string,
    topK = 12,
    videoId?: string,
    videoIds?: string[],
    minScore = 0.15
  ): Promise<SearchResponse> {
    const payload: TextSearchRequest = {
      query_text: queryText,
      top_k: topK,
      video_id: videoId,
      video_ids: videoIds && videoIds.length > 0 ? videoIds : undefined,
      min_score: minScore,
    }
    const response = await api.post<SearchResponse>('/search/text', payload)
    return response.data
  }

  /**
   * Execute Image-to-Video visual similarity search by uploading a query image
   */
  static async searchByImage(
    imageFile: File,
    topK = 12,
    videoId?: string,
    videoIds?: string[],
    minScore = 0.15
  ): Promise<SearchResponse> {
    const formData = new FormData()
    formData.append('image_file', imageFile)
    formData.append('top_k', topK.toString())
    formData.append('min_score', minScore.toString())
    if (videoId) {
      formData.append('video_id', videoId)
    }
    if (videoIds && videoIds.length > 0) {
      videoIds.forEach((vid) => formData.append('video_ids', vid))
    }

    const response = await api.post<SearchResponse>('/search/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  /**
   * Sync FAISS vector index from PostgreSQL database
   */
  static async buildIndex() {
    const response = await api.post('/search/build-index')
    return response.data
  }

  /**
   * Get status & statistics of FAISS vector index
   */
  static async getIndexStatus() {
    const response = await api.get('/search/index-status')
    return response.data
  }
}
