import React, { useState, useEffect, useCallback } from 'react'
import {
  ShieldCheck,
  Users,
  Video,
  Search,
  Database,
  Activity,
  RefreshCw,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  XCircle,
  UserCheck,
  Loader2,
  Film,
} from 'lucide-react'
import { AdminService, AdminMetrics, AdminUser, AdminJob } from '@/services/adminService'
import { toast } from 'sonner'

// ─── Helpers ────────────────────────────────────────────────────────────────

function formatBytes(bytes: number | null): string {
  if (!bytes) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

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

const STATUS_STYLES: Record<string, string> = {
  completed: 'bg-green-500/10 text-green-400 border-green-500/20',
  processing: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  pending: 'bg-slate-500/10 text-slate-400 border-slate-600',
  failed: 'bg-red-500/10 text-red-400 border-red-500/20',
}

const ROLE_STYLES: Record<string, string> = {
  admin: 'bg-red-500/10 text-red-400 border-red-500/20',
  investigator: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  viewer: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
}

// ─── Metric Card ─────────────────────────────────────────────────────────────

function MetricCard({
  label,
  value,
  sub,
  icon: Icon,
  color,
  loading,
}: {
  label: string
  value: string | number
  sub?: string
  icon: React.ComponentType<{ className?: string }>
  color: string
  loading: boolean
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 hover:border-slate-700 transition-colors">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{label}</span>
        <div className={`p-1.5 rounded-lg ${color}`}>
          <Icon className="h-4 w-4" />
        </div>
      </div>
      <div className={`text-3xl font-extrabold ${loading ? 'animate-pulse text-slate-700' : 'text-slate-100'}`}>
        {loading ? '—' : value}
      </div>
      {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
    </div>
  )
}

// ─── Main Component ──────────────────────────────────────────────────────────

type Tab = 'overview' | 'users' | 'jobs'

export const AdminPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('overview')
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null)
  const [metricsLoading, setMetricsLoading] = useState(true)
  const [metricsError, setMetricsError] = useState<string | null>(null)

  // Users state
  const [users, setUsers] = useState<AdminUser[]>([])
  const [usersLoading, setUsersLoading] = useState(false)
  const [usersTotal, setUsersTotal] = useState(0)
  const [usersPage, setUsersPage] = useState(1)
  const [usersPages, setUsersPages] = useState(1)
  const [roleFilter, setRoleFilter] = useState('')
  const [updatingUserId, setUpdatingUserId] = useState<string | null>(null)

  // Jobs state
  const [jobs, setJobs] = useState<AdminJob[]>([])
  const [jobsLoading, setJobsLoading] = useState(false)
  const [jobsTotal, setJobsTotal] = useState(0)
  const [jobsPage, setJobsPage] = useState(1)
  const [jobsPages, setJobsPages] = useState(1)
  const [statusFilter, setStatusFilter] = useState('')

  // ── Fetch metrics ──────────────────────────────────────────────
  const fetchMetrics = useCallback(async () => {
    try {
      setMetricsError(null)
      setMetricsLoading(true)
      const data = await AdminService.getMetrics()
      setMetrics(data)
    } catch (err: any) {
      setMetricsError(err?.message || 'Failed to load metrics')
    } finally {
      setMetricsLoading(false)
    }
  }, [])

  // ── Fetch users ────────────────────────────────────────────────
  const fetchUsers = useCallback(async (p = 1, role = '') => {
    setUsersLoading(true)
    try {
      const data = await AdminService.getUsers(p, 20, role || undefined)
      setUsers(data.items)
      setUsersTotal(data.total)
      setUsersPage(p)
      setUsersPages(data.pages)
    } catch (err: any) {
      toast.error('Failed to load users')
    } finally {
      setUsersLoading(false)
    }
  }, [])

  // ── Fetch jobs ─────────────────────────────────────────────────
  const fetchJobs = useCallback(async (p = 1, status = '') => {
    setJobsLoading(true)
    try {
      const data = await AdminService.getJobs(p, 30, status || undefined)
      setJobs(data.items)
      setJobsTotal(data.total)
      setJobsPage(p)
      setJobsPages(data.pages)
    } catch (err: any) {
      toast.error('Failed to load pipeline jobs')
    } finally {
      setJobsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchMetrics()
    const interval = setInterval(fetchMetrics, 30000)
    return () => clearInterval(interval)
  }, [fetchMetrics])

  useEffect(() => {
    if (activeTab === 'users') fetchUsers(1, roleFilter)
  }, [activeTab])

  useEffect(() => {
    if (activeTab === 'jobs') fetchJobs(1, statusFilter)
  }, [activeTab])

  // ── Update user ────────────────────────────────────────────────
  const handleUpdateUserRole = async (userId: string, newRole: string) => {
    setUpdatingUserId(userId)
    try {
      const updated = await AdminService.updateUser(userId, { role: newRole })
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)))
      toast.success(`Role updated to ${newRole}`)
    } catch (err: any) {
      toast.error('Failed to update role')
    } finally {
      setUpdatingUserId(null)
    }
  }

  const handleToggleActive = async (userId: string, currentActive: boolean) => {
    setUpdatingUserId(userId)
    try {
      const updated = await AdminService.updateUser(userId, { is_active: !currentActive })
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)))
      toast.success(updated.is_active ? 'User activated' : 'User deactivated')
    } catch (err: any) {
      toast.error('Failed to update user status')
    } finally {
      setUpdatingUserId(null)
    }
  }

  const tabs: { id: Tab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'users', label: `Users${metricsLoading ? '' : ` (${metrics?.users.total ?? 0})`}`, icon: Users },
    { id: 'jobs', label: `Jobs${metricsLoading ? '' : ` (${metrics?.videos.total ?? 0})`}`, icon: Film },
  ]

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight flex items-center gap-3">
            <div className="p-2 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            Admin Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            System metrics, user management, and pipeline monitoring
          </p>
        </div>
        <button
          onClick={fetchMetrics}
          disabled={metricsLoading}
          className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-slate-300 hover:bg-slate-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${metricsLoading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Error banner */}
      {metricsError && (
        <div className="flex items-center gap-2 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {metricsError}
        </div>
      )}

      {/* Tab bar */}
      <div className="flex gap-1 rounded-xl bg-slate-900/60 border border-slate-800 p-1 w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-slate-700 text-slate-100 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── OVERVIEW TAB ─────────────────────────────────────────── */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* User metrics */}
          <div>
            <h2 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-3">Users</h2>
            <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
              <MetricCard label="Total Users" value={metrics?.users.total ?? 0} sub={`${metrics?.users.active ?? 0} active`} icon={Users} color="bg-indigo-500/10 text-indigo-400" loading={metricsLoading} />
              <MetricCard label="Admins" value={metrics?.users.admin ?? 0} icon={ShieldCheck} color="bg-red-500/10 text-red-400" loading={metricsLoading} />
              <MetricCard label="Investigators" value={metrics?.users.investigator ?? 0} icon={UserCheck} color="bg-purple-500/10 text-purple-400" loading={metricsLoading} />
              <MetricCard label="Viewers" value={metrics?.users.viewer ?? 0} sub={`${metrics?.users.inactive ?? 0} inactive`} icon={Users} color="bg-blue-500/10 text-blue-400" loading={metricsLoading} />
            </div>
          </div>

          {/* Video & Search metrics */}
          <div>
            <h2 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-3">Videos & Search</h2>
            <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
              <MetricCard label="Total Videos" value={metrics?.videos.total ?? 0} sub={`${metrics?.videos.completed ?? 0} ready`} icon={Video} color="bg-green-500/10 text-green-400" loading={metricsLoading} />
              <MetricCard label="Processing" value={metrics?.videos.processing ?? 0} sub={`${metrics?.videos.pending ?? 0} pending`} icon={Activity} color="bg-yellow-500/10 text-yellow-400" loading={metricsLoading} />
              <MetricCard label="Failed" value={metrics?.videos.failed ?? 0} icon={XCircle} color="bg-red-500/10 text-red-400" loading={metricsLoading} />
              <MetricCard label="Total Searches" value={metrics?.searches.total ?? 0} icon={Search} color="bg-teal-500/10 text-teal-400" loading={metricsLoading} />
            </div>
          </div>

          {/* FAISS */}
          <div>
            <h2 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-3">FAISS Vector Index</h2>
            <div className="grid gap-4 grid-cols-2">
              <MetricCard label="Indexed Vectors" value={(metrics?.faiss_index.total_vectors ?? 0).toLocaleString()} sub="512D OpenCLIP embeddings" icon={Database} color="bg-purple-500/10 text-purple-400" loading={metricsLoading} />
              <MetricCard label="Vector Dimension" value={`${metrics?.faiss_index.dimension ?? 512}D`} sub="ViT-B-32 CLIP features" icon={Database} color="bg-slate-500/10 text-slate-400" loading={metricsLoading} />
            </div>
          </div>
        </div>
      )}

      {/* ── USERS TAB ────────────────────────────────────────────── */}
      {activeTab === 'users' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex items-center gap-3">
            <select
              value={roleFilter}
              onChange={(e) => {
                setRoleFilter(e.target.value)
                fetchUsers(1, e.target.value)
              }}
              className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Roles</option>
              <option value="admin">Admin</option>
              <option value="investigator">Investigator</option>
              <option value="viewer">Viewer</option>
            </select>
            <span className="text-xs text-slate-500">{usersTotal} users total</span>
          </div>

          {/* Table */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-800 text-xs text-slate-500 uppercase tracking-wider">
                    <th className="text-left px-5 py-3 font-semibold">User</th>
                    <th className="text-left px-4 py-3 font-semibold">Role</th>
                    <th className="text-left px-4 py-3 font-semibold">Status</th>
                    <th className="text-left px-4 py-3 font-semibold">Joined</th>
                    <th className="text-right px-5 py-3 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {usersLoading ? (
                    [...Array(5)].map((_, i) => (
                      <tr key={i} className="border-b border-slate-800/50">
                        <td colSpan={5} className="px-5 py-4">
                          <div className="h-6 rounded-lg bg-slate-800 animate-pulse" />
                        </td>
                      </tr>
                    ))
                  ) : users.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-16 text-center text-slate-500 text-sm">
                        No users found
                      </td>
                    </tr>
                  ) : (
                    users.map((user) => (
                      <tr
                        key={user.id}
                        className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors"
                      >
                        <td className="px-5 py-3.5">
                          <div className="font-medium text-slate-200">{user.full_name || user.email}</div>
                          {user.full_name && (
                            <div className="text-xs text-slate-500 truncate max-w-xs">{user.email}</div>
                          )}
                        </td>
                        <td className="px-4 py-3.5">
                          <select
                            value={user.role}
                            onChange={(e) => handleUpdateUserRole(user.id, e.target.value)}
                            disabled={updatingUserId === user.id}
                            className={`px-2.5 py-1 rounded-lg text-xs font-medium border cursor-pointer focus:outline-none ${ROLE_STYLES[user.role] || 'bg-slate-800 text-slate-400 border-slate-700'} bg-transparent`}
                          >
                            <option value="viewer">Viewer</option>
                            <option value="investigator">Investigator</option>
                            <option value="admin">Admin</option>
                          </select>
                        </td>
                        <td className="px-4 py-3.5">
                          <span
                            className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium border ${
                              user.is_active
                                ? 'bg-green-500/10 text-green-400 border-green-500/20'
                                : 'bg-slate-500/10 text-slate-400 border-slate-600'
                            }`}
                          >
                            {user.is_active ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-4 py-3.5 text-xs text-slate-500">
                          {formatRelativeTime(user.created_at)}
                        </td>
                        <td className="px-5 py-3.5 text-right">
                          {updatingUserId === user.id ? (
                            <Loader2 className="w-4 h-4 animate-spin text-slate-500 ml-auto" />
                          ) : (
                            <button
                              onClick={() => handleToggleActive(user.id, user.is_active)}
                              className={`px-3 py-1 rounded-lg text-xs border transition-colors ${
                                user.is_active
                                  ? 'bg-red-500/10 text-red-400 border-red-500/20 hover:bg-red-500/20'
                                  : 'bg-green-500/10 text-green-400 border-green-500/20 hover:bg-green-500/20'
                              }`}
                            >
                              {user.is_active ? 'Deactivate' : 'Activate'}
                            </button>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          {usersPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <button onClick={() => fetchUsers(usersPage - 1, roleFilter)} disabled={usersPage <= 1} className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300 disabled:opacity-40 hover:bg-slate-700 transition-colors">
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-xs text-slate-500">Page {usersPage} of {usersPages}</span>
              <button onClick={() => fetchUsers(usersPage + 1, roleFilter)} disabled={usersPage >= usersPages} className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300 disabled:opacity-40 hover:bg-slate-700 transition-colors">
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}

      {/* ── JOBS TAB ─────────────────────────────────────────────── */}
      {activeTab === 'jobs' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex items-center gap-3">
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value)
                fetchJobs(1, e.target.value)
              }}
              className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="processing">Processing</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
            <span className="text-xs text-slate-500">{jobsTotal} total jobs</span>
            <button
              onClick={() => fetchJobs(jobsPage, statusFilter)}
              disabled={jobsLoading}
              className="ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-slate-300 hover:bg-slate-700 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-3 h-3 ${jobsLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>

          {/* Table */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-800 text-xs text-slate-500 uppercase tracking-wider">
                    <th className="text-left px-5 py-3 font-semibold">Video</th>
                    <th className="text-left px-4 py-3 font-semibold">Status</th>
                    <th className="text-left px-4 py-3 font-semibold">Size</th>
                    <th className="text-left px-4 py-3 font-semibold">Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {jobsLoading ? (
                    [...Array(6)].map((_, i) => (
                      <tr key={i} className="border-b border-slate-800/50">
                        <td colSpan={4} className="px-5 py-4">
                          <div className="h-6 rounded-lg bg-slate-800 animate-pulse" />
                        </td>
                      </tr>
                    ))
                  ) : jobs.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="py-16 text-center text-slate-500 text-sm">
                        No pipeline jobs found
                      </td>
                    </tr>
                  ) : (
                    jobs.map((job) => (
                      <tr key={job.video_id} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                        <td className="px-5 py-3.5">
                          <div className="font-medium text-slate-200 truncate max-w-xs">{job.title}</div>
                          {job.error_message && (
                            <div className="text-xs text-red-400 truncate max-w-xs mt-0.5">{job.error_message}</div>
                          )}
                        </td>
                        <td className="px-4 py-3.5">
                          <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium border ${STATUS_STYLES[job.status] || 'bg-slate-500/10 text-slate-400 border-slate-600'}`}>
                            {job.status}
                          </span>
                        </td>
                        <td className="px-4 py-3.5 text-xs text-slate-400">
                          {formatBytes(job.file_size_bytes)}
                        </td>
                        <td className="px-4 py-3.5 text-xs text-slate-500">
                          {formatRelativeTime(job.updated_at)}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          {jobsPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <button onClick={() => fetchJobs(jobsPage - 1, statusFilter)} disabled={jobsPage <= 1} className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300 disabled:opacity-40 hover:bg-slate-700 transition-colors">
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-xs text-slate-500">Page {jobsPage} of {jobsPages}</span>
              <button onClick={() => fetchJobs(jobsPage + 1, statusFilter)} disabled={jobsPage >= jobsPages} className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300 disabled:opacity-40 hover:bg-slate-700 transition-colors">
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
