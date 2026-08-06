/**
 * Authentication Context
 * Provides authentication state and methods throughout the application
 */

import React, { createContext, useContext, useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { api } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';
import {
  User,
  Session,
  AuthContextType,
  SignupRequest,
  LoginRequest,
  ForgotPasswordRequest,
  AuthResponse,
  UserRole,
} from '@/types/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Zustand store actions
  const { setAuth, clearAuth, setRememberMe } = useAuthStore();

  /**
   * Sync state with Zustand store
   */
  useEffect(() => {
    if (user && session) {
      setAuth(user, session);
    } else {
      clearAuth();
    }
  }, [user, session, setAuth, clearAuth]);

  /**
   * Initialize authentication state from Supabase session
   */
  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session: supabaseSession } }) => {
      if (supabaseSession) {
        setSession({
          access_token: supabaseSession.access_token,
          refresh_token: supabaseSession.refresh_token,
          expires_in: supabaseSession.expires_in || 0,
          expires_at: supabaseSession.expires_at,
          token_type: 'bearer',
        });
        
        // Fetch user details from backend
        fetchUser(supabaseSession.access_token);
      } else {
        // Fallback for local development if no Supabase session
        setUser({
          id: 'dev-user-001',
          email: 'rathorerohitrr88@gmail.com',
          full_name: 'Rohit Rathore',
          role: UserRole.ADMIN,
          is_active: true,
          is_email_verified: true,
          can_upload_videos: true,
          can_manage_users: true,
          can_view_all_videos: true,
          created_at: new Date().toISOString(),
        });
        setSession({
          access_token: 'dev-mock-token',
          refresh_token: 'dev-mock-refresh',
          expires_in: 3600,
          token_type: 'bearer',
        });
        setIsLoading(false);
      }
    }).catch((err) => {
      console.warn('Supabase session check failed, operating in local dev mode:', err);
      setUser({
        id: 'dev-user-001',
        email: 'rathorerohitrr88@gmail.com',
        full_name: 'Rohit Rathore',
        role: UserRole.ADMIN,
        is_active: true,
        is_email_verified: true,
        can_upload_videos: true,
        can_manage_users: true,
        can_view_all_videos: true,
        created_at: new Date().toISOString(),
      });
      setSession({
        access_token: 'dev-mock-token',
        refresh_token: 'dev-mock-refresh',
        expires_in: 3600,
        token_type: 'bearer',
      });
      setIsLoading(false);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, supabaseSession) => {
      if (supabaseSession) {
        setSession({
          access_token: supabaseSession.access_token,
          refresh_token: supabaseSession.refresh_token,
          expires_in: supabaseSession.expires_in || 0,
          expires_at: supabaseSession.expires_at,
          token_type: 'bearer',
        });
        
        fetchUser(supabaseSession.access_token);
      } else {
        setIsLoading(false);
      }
    });

    return () => subscription.unsubscribe();
  }, []);


  /**
   * Fetch user details from backend API
   */
  const fetchUser = async (token: string) => {
    try {
      const response = await api.get<User>('/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      setUser(null);
      setSession(null);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Sign up a new user
   */
  const signup = async (data: SignupRequest): Promise<AuthResponse> => {
    try {
      const response = await api.post<AuthResponse>('/auth/signup', data);
      
      setUser(response.data.user);
      setSession(response.data.session);
      
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  /**
   * Log in an existing user
   */
  const login = async (data: LoginRequest): Promise<AuthResponse> => {
    try {
      const response = await api.post<AuthResponse>('/auth/login', data);
      
      setUser(response.data.user);
      setSession(response.data.session);
      
      // Store remember me preference
      setRememberMe(data.remember_me || false);
      
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  /**
   * Log out the current user
   */
  const logout = async (): Promise<void> => {
    try {
      if (session) {
        await api.post('/auth/logout', null, {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        });
      }
      
      await supabase.auth.signOut();
      
      setUser(null);
      setSession(null);
      clearAuth();
    } catch (error) {
      console.error('Logout error:', error);
      // Still clear local state even if API call fails
      setUser(null);
      setSession(null);
      clearAuth();
    }
  };

  /**
   * Request password reset email
   */
  const forgotPassword = async (
    data: ForgotPasswordRequest
  ): Promise<void> => {
    try {
      await api.post('/auth/forgot-password', data);
    } catch (error) {
      throw error;
    }
  };

  /**
   * Refresh user data from backend
   */
  const refreshUser = async (): Promise<void> => {
    if (session) {
      await fetchUser(session.access_token);
    }
  };

  const value: AuthContextType = {
    user,
    session,
    isLoading,
    isAuthenticated: !!user && !!session,
    signup,
    login,
    logout,
    forgotPassword,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to use authentication context
 * @throws Error if used outside AuthProvider
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}
