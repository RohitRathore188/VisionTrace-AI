/**
 * History Service
 * API client for the /search-history endpoints.
 */

import api from '@/lib/api'

export interface HistoryEntry {
  id: string
  query_text: string | null
  query_image_path: string | null
  search_type: 'text' | 'image' | 'hybrid' | 'metadata'
  filters: Record<string, unknown>
  result_count: number
  execution_time_ms: number
  created_at: string | null
  user_id: string
}

export interface HistoryListResponse {
  items: HistoryEntry[]
  total: number
  page: number
  page_size: number
  pages: number
}

export const HistoryService = {
  async getHistory(page = 1, pageSize = 20): Promise<HistoryListResponse> {
    const response = await api.get<HistoryListResponse>('/search-history', {
      params: { page, page_size: pageSize },
    })
    return response.data
  },

  async deleteEntry(id: string): Promise<void> {
    await api.delete(`/search-history/${id}`)
  },

  async clearHistory(): Promise<void> {
    await api.delete('/search-history/clear')
  },
}
