/**
 * Role-Based Access Control Hooks
 * Custom hooks for checking user roles and permissions
 */

import { useAuth } from './useAuth';
import { UserRole } from '@/types/auth';

/**
 * Hook to check if user has admin role
 */
export function useIsAdmin(): boolean {
  const { user } = useAuth();
  return user?.role === UserRole.ADMIN;
}

/**
 * Hook to check if user has investigator role or higher
 */
export function useIsInvestigator(): boolean {
  const { user } = useAuth();
  return user?.role === UserRole.INVESTIGATOR || user?.role === UserRole.ADMIN;
}

/**
 * Hook to check if user has viewer role or higher (any authenticated user)
 */
export function useIsViewer(): boolean {
  const { user } = useAuth();
  return !!user;
}

/**
 * Hook to check if user can upload videos
 */
export function useCanUploadVideos(): boolean {
  const { user } = useAuth();
  return user?.can_upload_videos || false;
}

/**
 * Hook to check if user can manage users
 */
export function useCanManageUsers(): boolean {
  const { user } = useAuth();
  return user?.can_manage_users || false;
}

/**
 * Hook to check if user can view all videos
 */
export function useCanViewAllVideos(): boolean {
  const { user } = useAuth();
  return user?.can_view_all_videos || false;
}

/**
 * Hook to check if user has any of the specified roles
 */
export function useHasRole(...roles: UserRole[]): boolean {
  const { user } = useAuth();
  return user ? roles.includes(user.role) : false;
}

/**
 * Hook to get all user permissions as an object
 */
export function usePermissions() {
  const { user } = useAuth();
  
  return {
    isAdmin: user?.role === UserRole.ADMIN,
    isInvestigator:
      user?.role === UserRole.INVESTIGATOR || user?.role === UserRole.ADMIN,
    isViewer: !!user,
    canUploadVideos: user?.can_upload_videos || false,
    canManageUsers: user?.can_manage_users || false,
    canViewAllVideos: user?.can_view_all_videos || false,
  };
}
