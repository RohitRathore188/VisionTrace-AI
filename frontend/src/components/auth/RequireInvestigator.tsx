/**
 * Require Investigator Component
 * Wrapper component that requires investigator or admin role to access routes
 */

import { RequireRole } from './RequireRole';
import { UserRole } from '@/types/auth';

interface RequireInvestigatorProps {
  children: React.ReactNode;
  fallbackPath?: string;
}

export function RequireInvestigator({
  children,
  fallbackPath,
}: RequireInvestigatorProps) {
  return (
    <RequireRole
      allowedRoles={[UserRole.INVESTIGATOR, UserRole.ADMIN]}
      fallbackPath={fallbackPath}
    >
      {children}
    </RequireRole>
  );
}
