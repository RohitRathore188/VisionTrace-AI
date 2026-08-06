/**
 * Type Definitions
 * Central export for all TypeScript types
 */

export * from './auth';
export * from './video';
export * from './frame';
export * from './object_detection';
export * from './bytetrack';
export * from './embedding';
export * from './search';

export type Theme = 'dark' | 'light' | 'system';

export interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
  label?: string;
  disabled?: boolean;
}

