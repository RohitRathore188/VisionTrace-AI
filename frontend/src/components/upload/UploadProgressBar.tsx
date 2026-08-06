import React from 'react'
import { Pause, Play, XCircle, CheckCircle2, AlertTriangle, Zap } from 'lucide-react'
import { UploadProgressState } from '@/types/video'
import { formatBytes } from '@/lib/videoValidation'

interface UploadProgressBarProps {
  progress: UploadProgressState
  onPause: () => void
  onResume: () => void
  onCancel: () => void
}

export const UploadProgressBar: React.FC<UploadProgressBarProps> = ({
  progress,
  onPause,
  onResume,
  onCancel,
}) => {
  const {
    bytesUploaded,
    totalBytes,
    percentage,
    speedMbps,
    etaSeconds,
    isPaused,
    isUploading,
    isCompleted,
    error,
  } = progress

  const formatEta = (seconds: number) => {
    if (seconds <= 0) return '0s'
    if (seconds < 60) return `${seconds}s`
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-xl">
      {/* Top Header Row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {isCompleted ? (
            <div className="w-8 h-8 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          ) : error ? (
            <div className="w-8 h-8 rounded-full bg-red-500/10 text-red-400 flex items-center justify-center border border-red-500/20">
              <AlertTriangle className="w-5 h-5" />
            </div>
          ) : (
            <div className="w-8 h-8 rounded-full bg-indigo-500/10 text-indigo-400 flex items-center justify-center border border-indigo-500/20">
              <Zap className="w-4 h-4 animate-pulse" />
            </div>
          )}

          <div>
            <h4 className="text-sm font-semibold text-slate-100">
              {isCompleted
                ? 'Upload Completed & Saved'
                : error
                ? 'Upload Failed'
                : isPaused
                ? 'Upload Paused'
                : 'Uploading Surveillance Video...'}
            </h4>
            <p className="text-xs text-slate-400">
              {formatBytes(bytesUploaded)} of {formatBytes(totalBytes)} ({percentage}%)
            </p>
          </div>
        </div>

        {/* Control Buttons */}
        {isUploading && !isCompleted && (
          <div className="flex items-center space-x-2">
            {isPaused ? (
              <button
                type="button"
                onClick={onResume}
                className="flex items-center space-x-1 text-xs font-semibold px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition shadow-sm"
              >
                <Play className="w-3.5 h-3.5" />
                <span>Resume</span>
              </button>
            ) : (
              <button
                type="button"
                onClick={onPause}
                className="flex items-center space-x-1 text-xs font-semibold px-3 py-1.5 rounded-lg bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/30 transition"
              >
                <Pause className="w-3.5 h-3.5" />
                <span>Pause</span>
              </button>
            )}

            <button
              type="button"
              onClick={onCancel}
              className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition"
              title="Cancel Upload"
            >
              <XCircle className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Progress Track */}
      <div className="space-y-1.5">
        <div className="relative h-2.5 w-full bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-300 rounded-full ${
              isCompleted
                ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                : error
                ? 'bg-red-500'
                : isPaused
                ? 'bg-amber-500'
                : 'bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-400 animate-pulse'
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>

        {/* Live Metrics Row */}
        {!isCompleted && !error && (
          <div className="flex justify-between items-center text-[11px] text-slate-400 pt-0.5">
            <span>
              Speed: <strong className="text-slate-200">{speedMbps} MB/s</strong>
            </span>
            <span>
              ETA: <strong className="text-slate-200">{formatEta(etaSeconds)}</strong>
            </span>
          </div>
        )}

        {error && <p className="text-xs text-red-400 mt-1 font-medium">{error}</p>}
      </div>
    </div>
  )
}
