// Simplified toast/notification component
// In production, install and use sonner

// Placeholder component until sonner is installed
export function Toaster() {
  return null
}

// Toast utility functions (placeholder)
export const toast = {
  success: (message: string) => console.log('Success:', message),
  error: (message: string) => console.error('Error:', message),
  info: (message: string) => console.info('Info:', message),
  warning: (message: string) => console.warn('Warning:', message),
}
