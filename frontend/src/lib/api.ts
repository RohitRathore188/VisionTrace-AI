import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { supabase } from './supabase'

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Create axios instance with default configuration
 */
const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Get current access token from Supabase session
 */
async function getAccessToken(): Promise<string | null> {
  try {
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.access_token) {
      return session.access_token
    }
  } catch (e) {
    console.warn('Supabase session check fallback:', e)
  }
  return 'dev-mock-token'
}

/**
 * Refresh access token using Supabase
 */
async function refreshAccessToken(): Promise<string | null> {
  try {
    const { data: { session }, error } = await supabase.auth.refreshSession()
    
    if (error) {
      console.error('Token refresh error:', error)
      return null
    }
    
    return session?.access_token || null
  } catch (error) {
    console.error('Token refresh failed:', error)
    return null
  }
}

/**
 * Request interceptor
 * - Adds authentication token from Supabase session
 * - Adds request ID for tracing
 */
api.interceptors.request.use(
  async (config) => {
    // Add auth token if available
    const token = await getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Add request ID for tracing
    config.headers['X-Request-ID'] = crypto.randomUUID()

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Response interceptor
 * - Handles token refresh on 401
 * - Transforms error responses
 * - Handles session expiration
 */
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }

    // Handle 401 Unauthorized - try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const newToken = await refreshAccessToken()
        
        if (newToken) {
          // Retry original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newToken}`
          }
          return api(originalRequest)
        } else {
          // Refresh failed - sign out and redirect to login
          await supabase.auth.signOut()
          
          // Only redirect if not already on auth page
          if (!window.location.pathname.startsWith('/auth')) {
            window.location.href = '/auth/login'
          }
          
          return Promise.reject({
            message: 'Session expired. Please login again.',
            code: 'SESSION_EXPIRED',
            status: 401,
            requestId: null,
            details: {},
          })
        }
      } catch (refreshError) {
        // Refresh failed - sign out and redirect to login
        await supabase.auth.signOut()
        
        if (!window.location.pathname.startsWith('/auth')) {
          window.location.href = '/auth/login'
        }
        
        return Promise.reject({
          message: 'Session expired. Please login again.',
          code: 'SESSION_EXPIRED',
          status: 401,
          requestId: null,
          details: {},
        })
      }
    }

    // Transform error response
    const errorData = error.response?.data as any
    const transformedError = {
      message: errorData?.error?.message || errorData?.message || error.message || 'An error occurred',
      code: errorData?.error?.code || errorData?.code || 'UNKNOWN_ERROR',
      status: error.response?.status || 500,
      requestId: errorData?.error?.request_id || errorData?.request_id || null,
      details: errorData?.error?.details || errorData?.details || {},
    }

    return Promise.reject(transformedError)
  }
)

/**
 * API error type
 */
export interface ApiError {
  message: string
  code: string
  status: number
  requestId: string | null
  details: Record<string, any>
}

/**
 * Check if error is an API error
 */
export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    'code' in error &&
    'status' in error
  )
}

export { api }
export default api
