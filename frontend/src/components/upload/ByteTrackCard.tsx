import React, { useState, useEffect, useCallback } from 'react'
import {
  Route,
  Play,
  RefreshCw,
  Compass,
  Activity,
} from 'lucide-react'
import { ByteTrackService } from '@/services/bytetrackService'
import { TrackSummary, TrackDetail, VisualizationResponse } from '@/types/bytetrack'
import { formatDuration } from '@/lib/videoValidation'

interface ByteTrackCardProps {
  videoId: string
  videoTitle: string
}

export const ByteTrackCard: React.FC<ByteTrackCardProps> = ({ videoId, videoTitle: _videoTitle }) => {
  const [tracks, setTracks] = useState<TrackSummary[]>([])
  const [selectedTrackDetail, setSelectedTrackDetail] = useState<TrackDetail | null>(null)
  const [visualization, setVisualization] = useState<VisualizationResponse | null>(null)
  const [isTracking, setIsTracking] = useState<boolean>(false)
  const [activeTrackId, setActiveTrackId] = useState<number | null>(null)

  const fetchTracksData = useCallback(async () => {
    try {
      const summaryList = await ByteTrackService.getTracks(videoId)
      setTracks(summaryList)

      const vizData = await ByteTrackService.getVisualization(videoId)
      setVisualization(vizData)
    } catch (err) {
      console.error('Failed to fetch ByteTrack tracks:', err)
    }
  }, [videoId])

  useEffect(() => {
    fetchTracksData()
  }, [fetchTracksData])

  const handleRunByteTrack = async () => {
    try {
      setIsTracking(true)
      await ByteTrackService.runTracking(videoId)
      await fetchTracksData()
    } catch (err: any) {
      console.error('ByteTrack tracking failed:', err)
    } finally {
      setIsTracking(false)
    }
  }

  const handleInspectTrack = async (trackId: number) => {
    try {
      setActiveTrackId(trackId)
      const detail = await ByteTrackService.getTrackDetail(videoId, trackId)
      setSelectedTrackDetail(detail)
    } catch (err) {
      console.error('Failed to inspect track detail:', err)
    }
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
            <Route className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">ByteTrack Multi-Object Tracking</h3>
            <p className="text-xs text-slate-400">
              Assign persistent object IDs & track spatial motion trajectories across sequential keyframes
            </p>
          </div>
        </div>

        <button
          onClick={handleRunByteTrack}
          disabled={isTracking}
          className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-lg shadow-blue-600/25 flex items-center justify-center space-x-2 transition disabled:opacity-50"
        >
          {isTracking ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
          <span>{isTracking ? 'Tracking Motion...' : 'Run ByteTrack Algorithm'}</span>
        </button>
      </div>

      {/* Interactive Motion Path Visualization Canvas */}
      {visualization && visualization.tracks.length > 0 && (
        <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-200">
              <Activity className="w-4 h-4 text-blue-400" />
              <span>Spatial Trajectory Motion Polylines</span>
            </div>
            <span className="text-[11px] text-slate-500 font-mono">
              Normalized Canvas Bounds (0.0 to 1.0)
            </span>
          </div>

          {/* SVG Motion Path Overlay Box */}
          <div className="relative w-full aspect-video bg-black/60 rounded-xl border border-slate-800/80 overflow-hidden flex items-center justify-center">
            <svg viewBox="0 0 1 1" className="w-full h-full transform scale-y-[-1]">
              <defs>
                <linearGradient id="pathGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#8b5cf6" />
                </linearGradient>
              </defs>

              {visualization.tracks.map((vt) => {
                const isSelected = activeTrackId === vt.track_id
                return (
                  <g key={vt.track_id} className="cursor-pointer" onClick={() => handleInspectTrack(vt.track_id)}>
                    <path
                      d={vt.svg_path}
                      fill="none"
                      stroke={isSelected ? '#ec4899' : 'url(#pathGradient)'}
                      strokeWidth={isSelected ? '0.008' : '0.004'}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="transition-all duration-300 hover:stroke-pink-400 hover:stroke-[0.008]"
                    />
                    {vt.points.map((pt, idx) => (
                      <circle
                        key={idx}
                        cx={pt.x}
                        cy={pt.y}
                        r={isSelected ? 0.008 : 0.005}
                        fill={isSelected ? '#ec4899' : '#60a5fa'}
                      />
                    ))}
                  </g>
                )
              })}
            </svg>
            <div className="absolute bottom-2 right-2 text-[10px] bg-black/80 px-2 py-1 rounded text-slate-400 font-mono">
              Click trajectory line to inspect
            </div>
          </div>
        </div>
      )}

      {/* Trajectory Summary Cards */}
      {tracks.length > 0 && (
        <div className="space-y-4 pt-2">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
              <Compass className="w-4 h-4 text-indigo-400" />
              <span>Tracked Motion Sequences ({tracks.length})</span>
            </h4>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {tracks.map((track) => (
              <div
                key={track.track_id}
                onClick={() => handleInspectTrack(track.track_id)}
                className={`bg-slate-950 border rounded-2xl p-4 space-y-3 cursor-pointer transition hover:scale-[1.02] ${
                  activeTrackId === track.track_id
                    ? 'border-pink-500 bg-pink-500/5'
                    : 'border-slate-800 hover:border-blue-500/60'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="w-7 h-7 rounded-lg bg-blue-500/10 text-blue-400 font-bold font-mono text-xs flex items-center justify-center border border-blue-500/20">
                      #{track.track_id}
                    </span>
                    <span className="font-bold text-slate-200 text-sm capitalize">{track.label}</span>
                  </div>

                  <span className="text-[11px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded">
                    {track.total_detections} keyframes
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400 font-mono border-t border-slate-800/60 pt-2">
                  <div>
                    <span>Duration: </span>
                    <strong className="text-slate-200">{formatDuration(track.duration_seconds)}</strong>
                  </div>
                  <div>
                    <span>Displacement: </span>
                    <strong className="text-blue-400">{(track.spatial_displacement * 100).toFixed(1)}%</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Track Detail Timeline Lightbox */}
      {selectedTrackDetail && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setSelectedTrackDetail(null)}
        >
          <div
            className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-4xl w-full space-y-5 max-h-[85vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-lg font-bold text-slate-100 flex items-center space-x-2">
                  <span>Track #{selectedTrackDetail.track_id} Trajectory Timeline</span>
                  <span className="text-xs bg-blue-500/10 text-blue-400 px-2.5 py-0.5 rounded-full border border-blue-500/20 uppercase font-mono">
                    {selectedTrackDetail.label}
                  </span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Tracked across {selectedTrackDetail.total_keyframes} keyframes ({formatDuration(selectedTrackDetail.start_timestamp)} → {formatDuration(selectedTrackDetail.end_timestamp)})
                </p>
              </div>

              <button
                onClick={() => setSelectedTrackDetail(null)}
                className="text-xs font-semibold px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl"
              >
                Close
              </button>
            </div>

            {/* Trajectory Points Timeline */}
            <div className="space-y-3">
              {selectedTrackDetail.trajectory.map((pt) => (
                <div
                  key={pt.object_id}
                  className="bg-slate-950 border border-slate-800/80 rounded-xl p-3 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded-lg bg-slate-900 border border-slate-800 overflow-hidden shrink-0 flex items-center justify-center">
                      {pt.crop_url ? (
                        <img src={pt.crop_url} alt="Crop" className="w-full h-full object-cover" />
                      ) : (
                        <span className="font-mono text-[10px] text-slate-500">#{pt.frame_number}</span>
                      )}
                    </div>

                    <div>
                      <p className="font-semibold text-slate-200">
                        Frame #{pt.frame_number} ({formatDuration(pt.timestamp_seconds)})
                      </p>
                      <p className="text-slate-400 font-mono text-[11px]">
                        Center: [{pt.center[0]}, {pt.center[1]}]
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 font-mono text-slate-400">
                    <span>Conf: <strong className="text-emerald-400">{Math.round(pt.confidence * 100)}%</strong></span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
