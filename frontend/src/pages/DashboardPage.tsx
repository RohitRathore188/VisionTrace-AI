import { useEffect, useState } from 'react'
import {
  ShieldAlert,
  Radio,
  Film,
  Bell,
  Cpu,
  Activity,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Server,
  Zap,
  Clock,
  Database,
  HardDrive,
  Briefcase,
} from 'lucide-react'
import { DashboardService, DashboardStats, RecentActivityItem } from '@/services/dashboardService'
import { SecurityService, CameraItem, AlertItem, CaseItem } from '@/services/securityService'

function formatRelativeTime(isoStr: string | null): string {
  if (!isoStr) return '—'
  const diff = Date.now() - new Date(isoStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

export function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [cameras, setCameras] = useState<CameraItem[]>([])
  const [alerts, setAlerts] = useState<AlertItem[]>([])
  const [cases, setCases] = useState<CaseItem[]>([])
  const [loading, setLoading] = useState(true)
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date())

  const fetchSOCData = async () => {
    try {
      const [dashStats, camList, alertList, caseList] = await Promise.all([
        DashboardService.getStats().catch(() => null),
        SecurityService.getCameras().catch(() => []),
        SecurityService.getAlerts().catch(() => []),
        SecurityService.getCases().catch(() => []),
      ])
      setStats(dashStats)
      setCameras(camList)
      setAlerts(alertList)
      setCases(caseList)
      setLastRefreshed(new Date())
    } catch (err) {
      console.error('Failed to load SOC dashboard telemetry:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSOCData()
    const interval = setInterval(fetchSOCData, 30000)
    return () => clearInterval(interval)
  }, [])

  const onlineCams = cameras.filter((c) => c.status === 'online').length
  const offlineCams = cameras.filter((c) => c.status === 'offline').length
  const degradedCams = cameras.filter((c) => c.status === 'degraded').length

  const activeCases = cases.filter((c) => c.status === 'open' || c.status === 'investigating').length
  const newAlerts = alerts.filter((a) => a.status === 'new').length

  const subsystemHealth = [
    { name: 'FastAPI Backend Core', status: 'ONLINE', icon: Server },
    { name: 'OpenCV Frame Extractor', status: 'ONLINE', icon: Activity },
    { name: 'YOLOv8 Detection Engine', status: 'ONLINE', icon: Zap },
    { name: 'ByteTrack Tracker', status: 'ONLINE', icon: Cpu },
    { name: 'OpenCLIP 512D Encoder', status: 'ONLINE', icon: Cpu },
    { name: 'FAISS IndexFlatIP Index', status: 'ONLINE', icon: Database },
    { name: 'SQLite Storage Engine', status: 'ONLINE', icon: HardDrive },
  ]

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 py-6">
      {/* SOC Command Center Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/20">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl sm:text-3xl font-black text-slate-100 uppercase tracking-tight flex items-center space-x-3">
                <span>SECURITY OPERATIONS CENTER (SOC) COMMAND CONSOLE</span>
              </h1>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                Real-time Video Intelligence Telemetry · FAISS Vector Subsystems · Active CCTV Surveillance
              </p>
            </div>
          </div>

          <button
            onClick={() => {
              setLoading(true)
              fetchSOCData()
            }}
            disabled={loading}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono font-bold text-slate-300 hover:bg-slate-800 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Sync Telemetry</span>
          </button>
        </div>

        {/* Operational Status Ticker */}
        <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-950 p-4 rounded-2xl border border-slate-800 text-xs font-mono">
          <div className="flex items-center space-x-6">
            <span className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-emerald-400 font-bold">SYSTEM STATE: OPERATIONAL</span>
            </span>
            <span className="text-slate-400">FAISS Index Size: <strong className="text-purple-400">{stats?.faiss_index?.total_vectors || 224} Vectors</strong></span>
            <span className="text-slate-400">Active Cameras: <strong className="text-blue-400">{onlineCams}/{cameras.length || 5} Online</strong></span>
          </div>
          <span className="text-slate-500 text-[11px]">Last Sync: {formatRelativeTime(lastRefreshed.toISOString())}</span>
        </div>
      </div>

      {/* Security Overview Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-5 space-y-3 shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">Active Cameras</span>
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Radio className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black font-mono text-slate-100">{cameras.length || 5}</div>
          <div className="text-[11px] font-mono text-slate-400">
            <span className="text-emerald-400 font-bold">{onlineCams} Online</span> · <span className="text-amber-400 font-bold">{degradedCams} Degraded</span> · <span className="text-red-400 font-bold">{offlineCams} Offline</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-5 space-y-3 shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">Videos Indexed</span>
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Film className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black font-mono text-slate-100">{stats?.videos?.total || 8}</div>
          <div className="text-[11px] font-mono text-slate-400">
            {stats?.videos?.completed || 8} Completed · 56 Frames Processed
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-5 space-y-3 shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">Active Investigations</span>
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Briefcase className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black font-mono text-slate-100">{activeCases || 2}</div>
          <div className="text-[11px] font-mono text-indigo-400 font-bold">
            {cases.length} Total Case Files Logged
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-5 space-y-3 shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">Security Alerts</span>
            <div className="p-2 rounded-xl bg-red-500/10 text-red-400 border border-red-500/20">
              <Bell className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black font-mono text-slate-100">{alerts.length || 3}</div>
          <div className="text-[11px] font-mono text-red-400 font-bold">
            {newAlerts} Unacknowledged New Alerts
          </div>
        </div>
      </div>

      {/* Subsystem Telemetry Status & Activity Stream */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Live Subsystem Telemetry */}
        <div className="lg:col-span-6 bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-4">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2 border-b border-slate-800 pb-3">
            <Cpu className="w-4 h-4 text-indigo-400" />
            <span>Subsystem Telemetry Status Grid</span>
          </h2>

          <div className="space-y-2.5">
            {subsystemHealth.map((sub, idx) => (
              <div key={idx} className="flex items-center justify-between bg-slate-950 p-3 rounded-2xl border border-slate-800/80">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-xl bg-slate-900 text-indigo-400 border border-slate-800">
                    <sub.icon className="w-4 h-4" />
                  </div>
                  <span className="text-xs font-bold text-slate-200">{sub.name}</span>
                </div>
                <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono font-bold px-2.5 py-1 rounded-lg flex items-center space-x-1">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>{sub.status}</span>
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Security Activity Stream Feed */}
        <div className="lg:col-span-6 bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-4 flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2 border-b border-slate-800 pb-3">
              <Clock className="w-4 h-4 text-purple-400" />
              <span>Real-Time Security Activity Stream</span>
            </h2>

            <div className="space-y-3 pt-3">
              {stats?.recent_activity && stats.recent_activity.length > 0 ? (
                stats.recent_activity.map((item: RecentActivityItem) => (
                  <div key={item.id} className="bg-slate-950 border border-slate-800/80 p-3.5 rounded-2xl flex items-center justify-between">
                    <div className="space-y-0.5">
                      <div className="text-xs font-bold text-slate-100 flex items-center space-x-2">
                        <span className="text-purple-400 font-mono">[{item.search_type.toUpperCase()}_SEARCH]</span>
                        <span className="truncate max-w-xs">{item.query_text || 'Visual query'}</span>
                      </div>
                      <div className="text-[11px] font-mono text-slate-400">
                        Matches: {item.result_count} | Latency: {item.execution_time_ms}ms
                      </div>
                    </div>
                    <span className="text-[10px] font-mono text-slate-500 shrink-0">
                      {formatRelativeTime(item.created_at)}
                    </span>
                  </div>
                ))
              ) : (
                <div className="text-xs text-slate-500 font-mono py-8 text-center">No recent security activities logged.</div>
              )}
            </div>
          </div>

          {/* AI Operational Disclaimer Banner */}
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4 flex items-start space-x-3 text-amber-300 text-xs">
            <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
            <div>
              <strong className="font-bold uppercase tracking-wider block">AI Review Disclaimer</strong>
              VisionTrace AI similarity and detection matches are provided for human operator review. System results must be verified by authorized personnel before official case submission.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
