/**
 * Authentication Store
 * Zustand store for authentication state management
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, Session } from '@/types/auth'

interface AuthState {
  user: User | null
  session: Session | null
  isAuthenticated: boolean
  rememberMe: boolean
}

interface AuthActions {
  setUser: (user: User | null) => void
  setSession: (session: Session | null) => void
  setAuth: (user: User | null, session: Session | null) => void
  setRememberMe: (remember: boolean) => void
  clearAuth: () => void
  updateUser: (updates: Partial<User>) => void
}

type AuthStore = AuthState & AuthActions

const initialState: AuthState = {
  user: null,
  session: null,
  isAuthenticated: false,
  rememberMe: false,
}

/**
 * Authentication store
 * Persists user session and preferences to localStorage
 */
export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      /**
       * Set user information
       */
      setUser: (user) => {
        set({
          user,
          isAuthenticated: !!user,
        })
      },

      /**
       * Set session information
       */
      setSession: (session) => {
        set({ session })
      },

      /**
       * Set both user and session
       */
      setAuth: (user, session) => {
        set({
          user,
          session,
          isAuthenticated: !!user && !!session,
        })
      },

      /**
       * Set remember me preference
       */
      setRememberMe: (remember) => {
        set({ rememberMe: remember })
      },

      /**
       * Clear all authentication state
       */
      clearAuth: () => {
        set({
          user: null,
          session: null,
          isAuthenticated: false,
        })
      },

      /**
       * Update user information partially
       */
      updateUser: (updates) => {
        const currentUser = get().user
        if (currentUser) {
          set({
            user: { ...currentUser, ...updates },
          })
        }
      },
    }),
    {
      name: 'visiontrace-auth-storage',
      // Only persist user and rememberMe, not session (security)
      partialize: (state) => ({
        user: state.rememberMe ? state.user : null,
        rememberMe: state.rememberMe,
      }),
    }
  )
)

/**
 * Selectors for auth store
 */
export const authSelectors = {
  user: (state: AuthStore) => state.user,
  session: (state: AuthStore) => state.session,
  isAuthenticated: (state: AuthStore) => state.isAuthenticated,
  rememberMe: (state: AuthStore) => state.rememberMe,
  userRole: (state: AuthStore) => state.user?.role,
  userEmail: (state: AuthStore) => state.user?.email,
  userName: (state: AuthStore) => state.user?.full_name || state.user?.email,
  canUploadVideos: (state: AuthStore) => state.user?.can_upload_videos || false,
  canManageUsers: (state: AuthStore) => state.user?.can_manage_users || false,
  canViewAllVideos: (state: AuthStore) => state.user?.can_view_all_videos || false,
}
