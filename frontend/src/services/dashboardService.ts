/**
 * Dashboard Service
 * Fetches real-time aggregated stats from the /dashboard/stats endpoint.
 */

import api from '@/lib/api'

export interface VideoStats {
  total: number
  pending: number
  processing: number
  completed: number
  failed: number
}

export interface SearchStats {
  total: number
}

export interface FaissStats {
  total_vectors: number
  dimension: number
}

export interface RecentActivityItem {
  id: string
  query_text: string | null
  search_type: 'text' | 'image' | 'hybrid' | 'metadata'
  result_count: number
  execution_time_ms: number
  created_at: string | null
}

export interface DashboardStats {
  videos: VideoStats
  searches: SearchStats
  faiss_index: FaissStats
  recent_activity: RecentActivityItem[]
  execution_time_ms: number
}

export const DashboardService = {
  async getStats(): Promise<DashboardStats> {
    const response = await api.get<DashboardStats>('/dashboard/stats')
    return response.data
  },
}
