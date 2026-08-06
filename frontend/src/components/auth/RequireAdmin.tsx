/**
 * Require Admin Component
 * Wrapper component that requires admin role to access routes
 */

import { RequireRole } from './RequireRole';
import { UserRole } from '@/types/auth';

interface RequireAdminProps {
  children: React.ReactNode;
  fallbackPath?: string;
}

export function RequireAdmin({ children, fallbackPath }: RequireAdminProps) {
  return (
    <RequireRole allowedRoles={[UserRole.ADMIN]} fallbackPath={fallbackPath}>
      {children}
    </RequireRole>
  );
}
