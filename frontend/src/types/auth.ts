/**
 * Authentication Type Definitions
 * Types for user, session, and authentication-related data
 */

export enum UserRole {
  ADMIN = 'admin',
  INVESTIGATOR = 'investigator',
  VIEWER = 'viewer',
}

export interface User {
  id: string;
  email: string;
  full_name?: string | null;
  role: UserRole;
  is_active: boolean;
  is_email_verified: boolean;
  created_at: string;
  last_login_at?: string | null;
  can_upload_videos: boolean;
  can_manage_users: boolean;
  can_view_all_videos: boolean;
}

export interface Session {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  expires_at?: number | null;
  token_type: string;
}

export interface AuthResponse {
  user: User;
  session: Session;
  message?: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name?: string;
  role?: UserRole;
}

export interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface AuthContextType {
  user: User | null;
  session: Session | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signup: (data: SignupRequest) => Promise<AuthResponse>;
  login: (data: LoginRequest) => Promise<AuthResponse>;
  logout: () => Promise<void>;
  forgotPassword: (data: ForgotPasswordRequest) => Promise<void>;
  refreshUser: () => Promise<void>;
}
