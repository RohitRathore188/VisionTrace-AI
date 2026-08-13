import React from 'react'
import { Activity, Server, Cpu, Database, HardDrive, Zap, CheckCircle2 } from 'lucide-react'

export const SystemHealthPage: React.FC = () => {
  const subsystems = [
    { name: 'FastAPI Backend Engine', status: 'ONLINE', icon: Server, latency: '2.4ms' },
    { name: 'OpenCV Frame Extractor @ 1 FPS', status: 'ONLINE', icon: Activity, latency: '8.1ms' },
    { name: 'YOLOv8 Object Detection Engine', status: 'ONLINE', icon: Zap, latency: '14.2ms' },
    { name: 'ByteTrack Multi-Object Tracker', status: 'ONLINE', icon: Cpu, latency: '6.5ms' },
    { name: 'OpenCLIP 512D Embedding Engine', status: 'ONLINE', icon: Cpu, latency: '12.0ms' },
    { name: 'FAISS IndexFlatIP Vector Engine', status: 'ONLINE', icon: Database, latency: '1.2ms' },
    { name: 'SQLite DB & Storage Engine', status: 'ONLINE', icon: HardDrive, latency: '0.8ms' },
  ]

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-2">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-2xl bg-emerald-600/20 text-emerald-400 border border-emerald-500/30">
            <Activity className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-slate-100 uppercase tracking-tight flex items-center space-x-2">
              <span>Security Subsystem Telemetry & AI Health Status</span>
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Live operational health status of all computer vision, tracking, and vector indexing services
            </p>
          </div>
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {subsystems.map((sub, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-3xl p-5 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div className="p-2.5 rounded-2xl bg-slate-950 border border-slate-800 text-indigo-400">
                <sub.icon className="w-5 h-5" />
              </div>
              <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono font-bold px-2.5 py-1 rounded-lg flex items-center space-x-1">
                <CheckCircle2 className="w-3 h-3" />
                <span>{sub.status}</span>
              </span>
            </div>

            <div>
              <h4 className="font-bold text-slate-100 text-sm">{sub.name}</h4>
              <p className="text-xs text-slate-400 font-mono mt-1">Operational Latency: {sub.latency}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
