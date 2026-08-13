/**
 * Admin Service
 * API client for admin-only endpoints: metrics, user management, and pipeline jobs.
 */

import api from '@/lib/api'

export interface AdminMetrics {
  users: {
    total: number
    admin: number
    investigator: number
    viewer: number
    active: number
    inactive: number
  }
  videos: {
    total: number
    pending: number
    processing: number
    completed: number
    failed: number
  }
  searches: { total: number }
  faiss_index: { total_vectors: number; dimension: number }
  execution_time_ms: number
}

export interface AdminUser {
  id: string
  email: string
  full_name: string | null
  role: 'admin' | 'investigator' | 'viewer'
  is_active: boolean
  is_email_verified: boolean
  last_login_at: string | null
  created_at: string | null
}

export interface AdminUserListResponse {
  items: AdminUser[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface AdminJob {
  video_id: string
  title: string
  status: string
  user_id: string
  file_size_bytes: number | null
  duration_seconds: number | null
  error_message: string | null
  created_at: string | null
  updated_at: string | null
}

export interface AdminJobListResponse {
  items: AdminJob[]
  total: number
  page: number
  page_size: number
  pages: number
}

export const AdminService = {
  async getMetrics(): Promise<AdminMetrics> {
    const response = await api.get<AdminMetrics>('/admin/metrics')
    return response.data
  },

  async getUsers(
    page = 1,
    pageSize = 20,
    role?: string,
  ): Promise<AdminUserListResponse> {
    const response = await api.get<AdminUserListResponse>('/admin/users', {
      params: { page, page_size: pageSize, role },
    })
    return response.data
  },

  async updateUser(
    userId: string,
    updates: { role?: string; is_active?: boolean },
  ): Promise<AdminUser> {
    const response = await api.put<AdminUser>(`/admin/users/${userId}`, updates)
    return response.data
  },

  async getJobs(
    page = 1,
    pageSize = 30,
    status?: string,
  ): Promise<AdminJobListResponse> {
    const response = await api.get<AdminJobListResponse>('/admin/jobs', {
      params: { page, page_size: pageSize, status },
    })
    return response.data
  },
}
