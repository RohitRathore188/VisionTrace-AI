import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  UploadCloud,
  Video,
  Search,
  History,
  Settings,
  ChevronLeft,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import type { NavItem } from '@/types'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

const navigation: NavItem[] = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    title: 'Video Upload',
    href: '/upload',
    icon: UploadCloud,
  },
  {
    title: 'FAISS Search',
    href: '/search',
    icon: Search,
  },
  {
    title: 'Videos',
    href: '/videos',
    icon: Video,
  },
  {
    title: 'History',
    href: '/history',
    icon: History,
  },
  {
    title: 'Settings',
    href: '/settings',
    icon: Settings,
  },
]

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r bg-card transition-transform duration-300 lg:sticky lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Logo and toggle */}
        <div className="flex h-16 items-center justify-between border-b px-6">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <Video className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold">VisionTrace AI</span>
              <span className="text-xs text-muted-foreground">v1.0.0</span>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className="h-8 w-8"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 overflow-y-auto p-4">
          {navigation.map((item) => (
            <NavLink
              key={item.href}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  item.disabled
                    ? 'cursor-not-allowed opacity-50'
                    : isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )
              }
              onClick={(e) => item.disabled && e.preventDefault()}
            >
              {item.icon && <item.icon className="h-5 w-5 shrink-0" />}
              <span>{item.title}</span>
              {item.label && (
                <span className="ml-auto text-xs">{item.label}</span>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="border-t p-4">
          <div className="rounded-lg bg-muted p-3">
            <p className="text-xs text-muted-foreground">
              Need help? Check out our{' '}
              <a href="#" className="font-medium text-primary hover:underline">
                documentation
              </a>
            </p>
          </div>
        </div>
      </aside>
    </>
  )
}
