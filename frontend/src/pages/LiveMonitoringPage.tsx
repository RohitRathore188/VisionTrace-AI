import React, { useState, useEffect } from 'react'
import { SecurityService, CameraItem } from '@/services/securityService'
import { Radio, Film } from 'lucide-react'

export const LiveMonitoringPage: React.FC = () => {
  const [cameras, setCameras] = useState<CameraItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchCameras = async () => {
    try {
      const data = await SecurityService.getCameras()
      setCameras(data)
    } catch (err) {
      console.error('Failed to load surveillance cameras:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchCameras()
  }, [])

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-2">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-2xl bg-blue-600/20 text-blue-400 border border-blue-500/30">
            <Radio className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-slate-100 uppercase tracking-tight flex items-center space-x-2">
              <span>Live Surveillance Monitoring & Camera Node Grid</span>
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Real-time CCTV stream channels, operational status telemetry, and hardware node health
            </p>
          </div>
        </div>
      </div>

      {/* Camera Grid */}
      {isLoading ? (
        <div className="py-16 text-center text-xs text-slate-400">Loading camera nodes...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cameras.map((cam) => (
            <div key={cam.id} className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl space-y-3 p-4 flex flex-col justify-between">
              <div className="space-y-3">
                {/* Simulated Video Feed Viewport */}
                <div className="aspect-video bg-black rounded-2xl relative flex items-center justify-center overflow-hidden border border-slate-800">
                  <div className="absolute top-3 left-3 bg-black/80 backdrop-blur-md px-2.5 py-1 rounded-lg text-[10px] font-mono font-bold text-slate-100 border border-slate-700 flex items-center space-x-1.5">
                    <span className={`w-2 h-2 rounded-full ${cam.status === 'online' ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
                    <span>{cam.name}</span>
                  </div>

                  <div className="absolute top-3 right-3 bg-black/80 backdrop-blur-md px-2 py-0.5 rounded text-[10px] font-mono text-indigo-300">
                    {cam.resolution} @ {cam.fps} FPS
                  </div>

                  <div className="text-center space-y-2 p-4">
                    <Film className="w-8 h-8 text-slate-700 mx-auto" />
                    <p className="text-[11px] font-mono text-slate-500 uppercase">
                      {cam.status === 'online' ? 'RTSP Stream Simulated' : 'Channel Offline'}
                    </p>
                  </div>
                </div>

                <div className="space-y-1 px-1">
                  <h4 className="font-bold text-slate-100 text-sm">{cam.name}</h4>
                  <p className="text-xs text-slate-400 font-mono">Location: {cam.location} — Zone: {cam.zone}</p>
                </div>
              </div>

              <div className="border-t border-slate-800/80 pt-3 flex items-center justify-between text-[11px] font-mono">
                <span className="text-slate-400">Node Status:</span>
                <span className={`font-bold uppercase ${cam.status === 'online' ? 'text-emerald-400' : 'text-red-400'}`}>
                  {cam.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
