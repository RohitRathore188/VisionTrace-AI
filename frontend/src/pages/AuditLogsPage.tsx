import React, { useState, useEffect } from 'react'
import { SecurityService, AuditLogItem } from '@/services/securityService'
import { FileCode } from 'lucide-react'

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchLogs = async () => {
    try {
      const data = await SecurityService.getAuditLogs()
      setLogs(data)
    } catch (err) {
      console.error('Failed to load audit logs:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchLogs()
  }, [])

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-2">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
            <FileCode className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-slate-100 uppercase tracking-tight flex items-center space-x-2">
              <span>Immutable System Audit Trail Inspector</span>
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Read-only immutable log trail tracking all user operations, search queries, and evidence accesses
            </p>
          </div>
        </div>
      </div>

      {/* Log Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
        {isLoading ? (
          <div className="py-16 text-center text-xs text-slate-400">Loading audit trail logs...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-950 border-b border-slate-800 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                <tr>
                  <th className="p-4">Timestamp</th>
                  <th className="p-4">User Email</th>
                  <th className="p-4">Action</th>
                  <th className="p-4">Resource Target</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Details payload</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80 text-slate-300">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-950/60 transition">
                    <td className="p-4 text-slate-400">{new Date(log.created_at).toLocaleString()}</td>
                    <td className="p-4 text-indigo-400 font-bold">{log.user_email}</td>
                    <td className="p-4 font-bold text-purple-300">{log.action}</td>
                    <td className="p-4 text-slate-300">{log.resource_type}:{log.resource_id}</td>
                    <td className="p-4">
                      <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold px-2 py-0.5 rounded-md">
                        {log.result_status}
                      </span>
                    </td>
                    <td className="p-4 text-[10px] text-slate-400 truncate max-w-xs">
                      {JSON.stringify(log.details_json)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
