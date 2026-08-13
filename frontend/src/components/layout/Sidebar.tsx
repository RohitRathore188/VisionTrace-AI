import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import {
  ShieldAlert,
  Activity,
  Film,
  Search,
  Briefcase,
  Bell,
  Eye,
  UserCheck,
  Car,
  Box,
  TrendingUp,
  Lock,
  FileText,
  Download,
  FileCode,
  Settings,
  ChevronLeft,
  ShieldCheck,
  Radio,
  Sliders,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { usePermissions } from '@/hooks/useRole'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

interface NavSection {
  title: string
  items: {
    title: string
    href: string
    icon: any
    badge?: string
    badgeColor?: string
  }[]
}

const navSections: NavSection[] = [
  {
    title: 'OPERATIONS',
    items: [
      { title: 'Command Center', href: '/dashboard', icon: ShieldAlert, badge: 'SOC', badgeColor: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' },
      { title: 'Live Monitoring', href: '/monitoring', icon: Radio, badge: '5 CAMs', badgeColor: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
      { title: 'Video Evidence', href: '/videos', icon: Film },
      { title: 'Investigation', href: '/investigate', icon: Eye },
      { title: 'FAISS AI Search', href: '/search', icon: Search, badge: 'FAISS', badgeColor: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
      { title: 'Cases', href: '/cases', icon: Briefcase },
      { title: 'Alerts', href: '/alerts', icon: Bell, badge: '3 NEW', badgeColor: 'bg-red-500/20 text-red-400 border-red-500/30 font-mono' },
    ],
  },
  {
    title: 'INTELLIGENCE',
    items: [
      { title: 'Person Search', href: '/intelligence/person', icon: UserCheck },
      { title: 'Vehicle Search', href: '/intelligence/vehicle', icon: Car },
      { title: 'Object Intelligence', href: '/intelligence/objects', icon: Box },
      { title: 'ByteTrack Tracking', href: '/intelligence/tracking', icon: Sliders },
      { title: 'Security Analytics', href: '/analytics', icon: TrendingUp },
    ],
  },
  {
    title: 'EVIDENCE & REPORTS',
    items: [
      { title: 'Evidence Locker', href: '/evidence-locker', icon: Lock, badge: 'SHA-256', badgeColor: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30' },
      { title: 'Case Reports', href: '/reports', icon: FileText },
      { title: 'Export Center', href: '/export-center', icon: Download },
    ],
  },
  {
    title: 'SYSTEM & AUDIT',
    items: [
      { title: 'Audit Logs', href: '/audit-logs', icon: FileCode },
      { title: 'System Health', href: '/system-health', icon: Activity, badge: 'ONLINE', badgeColor: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' },
      { title: 'Settings', href: '/settings', icon: Settings },
    ],
  },
]

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const { isAdmin } = usePermissions()

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/80 backdrop-blur-sm lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Security Operations Command Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-slate-800 bg-slate-950 transition-transform duration-300 lg:sticky lg:translate-x-0 shadow-2xl',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Header Logo */}
        <div className="flex h-16 items-center justify-between border-b border-slate-800 px-5">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-600/30">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-black tracking-tight text-slate-100 uppercase">VISIONTRACE AI</span>
              <span className="text-[10px] font-mono font-bold text-indigo-400 tracking-wider">SECURITY INTELLIGENCE v2.0</span>
            </div>
          </div>

          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className="h-8 w-8 text-slate-400 hover:text-white hover:bg-slate-900"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
        </div>

        {/* Navigation Sections */}
        <nav className="flex-1 space-y-6 overflow-y-auto p-4 scrollbar-thin scrollbar-thumb-slate-800">
          {navSections.map((section) => (
            <div key={section.title} className="space-y-1">
              <p className="px-3 text-[10px] font-bold uppercase tracking-widest text-slate-400/80 mb-2">
                {section.title}
              </p>

              {section.items.map((item) => (
                <NavLink
                  key={item.href}
                  to={item.href}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 rounded-xl px-3 py-2 text-xs font-semibold transition-all duration-200 border',
                      isActive
                        ? 'bg-indigo-600/20 text-indigo-300 border-indigo-500/40 shadow-lg shadow-indigo-600/10'
                        : 'text-slate-400 border-transparent hover:bg-slate-900 hover:text-slate-200 hover:border-slate-800'
                    )
                  }
                >
                  <item.icon className="h-4 w-4 shrink-0 text-slate-400" />
                  <span className="truncate">{item.title}</span>

                  {item.badge && (
                    <span className={cn('ml-auto text-[9px] font-mono font-bold px-2 py-0.5 rounded-md border', item.badgeColor)}>
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              ))}
            </div>
          ))}

          {/* Admin Navigation link */}
          {isAdmin && (
            <div className="pt-3 border-t border-slate-800/80">
              <p className="px-3 mb-2 text-[10px] font-bold uppercase tracking-widest text-red-400/80">
                ADMINISTRATION
              </p>
              <NavLink
                to="/admin"
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-xl px-3 py-2 text-xs font-semibold transition-all border',
                    isActive
                      ? 'bg-red-500/20 text-red-300 border-red-500/40'
                      : 'text-slate-400 border-transparent hover:bg-slate-900 hover:text-slate-200'
                  )
                }
              >
                <ShieldCheck className="h-4 w-4 shrink-0 text-red-400" />
                <span>Admin Console</span>
              </NavLink>
            </div>
          )}
        </nav>

        {/* Footer Operational Badge */}
        <div className="border-t border-slate-800 p-4">
          <div className="rounded-xl bg-slate-900/90 border border-slate-800 p-3 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold text-slate-400">SOC CENTER</span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-[10px] font-mono font-bold text-emerald-400">SECURE</span>
              </span>
            </div>
            <p className="text-[11px] font-mono text-slate-400">
              Authorized Personnel Only
            </p>
          </div>
        </div>
      </aside>
    </>
  )
}
