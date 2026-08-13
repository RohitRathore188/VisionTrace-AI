import React, { useState, useEffect } from 'react'
import { SecurityService, AlertItem } from '@/services/securityService'
import {
  Bell,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Camera,
} from 'lucide-react'

export const AlertCenterPage: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchAlerts = async () => {
    try {
      const data = await SecurityService.getAlerts()
      setAlerts(data)
    } catch (err) {
      console.error('Failed to load security alerts:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchAlerts()
  }, [])

  const handleAcknowledge = async (id: string) => {
    try {
      const updated = await SecurityService.acknowledgeAlert(id)
      setAlerts(alerts.map((a) => (a.id === updated.id ? updated : a)))
    } catch (err) {
      console.error('Failed to acknowledge alert:', err)
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-2">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-2xl bg-red-600/20 text-red-400 border border-red-500/30">
            <Bell className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-slate-100 uppercase tracking-tight flex items-center space-x-2">
              <span>Security Alert Center & Threat Detection Feed</span>
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Real-time security events, restricted perimeter detections, and AI operational alerts
            </p>
          </div>
        </div>
      </div>

      {/* Alert Feed List */}
      <div className="space-y-3">
        {isLoading ? (
          <div className="py-16 text-center text-xs text-slate-400">Loading security alerts...</div>
        ) : alerts.length === 0 ? (
          <div className="py-16 text-center text-xs text-slate-500 border border-dashed border-slate-800 rounded-3xl">
            No active security alerts
          </div>
        ) : (
          alerts.map((item) => (
            <div
              key={item.id}
              className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-3xl p-5 shadow-xl flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 transition"
            >
              <div className="flex items-start space-x-4">
                <div
                  className={`p-3 rounded-2xl shrink-0 ${
                    item.severity === 'critical'
                      ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                      : item.severity === 'warning'
                      ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                  }`}
                >
                  <AlertTriangle className="w-6 h-6" />
                </div>

                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-mono font-bold text-slate-400">{item.alert_id}</span>
                    <span className="text-sm font-bold text-slate-100">{item.alert_type}</span>
                  </div>

                  <div className="flex items-center space-x-3 text-xs font-mono text-slate-400">
                    <span className="flex items-center space-x-1">
                      <Camera className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{item.camera_name}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <Clock className="w-3.5 h-3.5 text-purple-400" />
                      <span>@{item.timestamp_seconds}s</span>
                    </span>
                    {item.detected_object_label && (
                      <span className="bg-slate-950 px-2 py-0.5 rounded text-[11px] text-emerald-400 border border-slate-800">
                        Class: {item.detected_object_label} ({((item.confidence || 0.85) * 100).toFixed(0)}%)
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Status & Action */}
              <div className="flex items-center space-x-3 shrink-0 self-end sm:self-auto">
                {item.status === 'acknowledged' ? (
                  <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold px-3 py-1.5 rounded-xl flex items-center space-x-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>ACKNOWLEDGED</span>
                  </span>
                ) : (
                  <button
                    onClick={() => handleAcknowledge(item.id)}
                    className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white text-xs font-bold shadow-lg shadow-red-600/25 transition"
                  >
                    Acknowledge Alert
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
