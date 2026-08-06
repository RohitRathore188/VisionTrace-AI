import React, { useState, useEffect, useCallback } from 'react'
import {
  Scissors,
  Play,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Image as ImageIcon,
  Sliders,
  Sparkles,
} from 'lucide-react'
import { FrameService } from '@/services/frameService'
import { FrameExtractionProgress, Frame } from '@/types/frame'
import { formatDuration } from '@/lib/videoValidation'

interface FrameExtractionCardProps {
  videoId: string
  videoTitle: string
  onCompleted?: () => void
}

export const FrameExtractionCard: React.FC<FrameExtractionCardProps> = ({
  videoId,
  videoTitle: _videoTitle,
  onCompleted,
}) => {
  const [intervalSeconds, setIntervalSeconds] = useState<number>(1.0)
  const [progress, setProgress] = useState<FrameExtractionProgress | null>(null)
  const [isExtracting, setIsExtracting] = useState<boolean>(false)
  const [frames, setFrames] = useState<Frame[]>([])
  const [selectedFrame, setSelectedFrame] = useState<Frame | null>(null)

  const fetchFrames = useCallback(async () => {
    try {
      const data = await FrameService.getExtractedFrames(videoId, 1, 60)
      setFrames(data.items || [])
    } catch (err) {
      console.error('Failed to fetch frames:', err)
    }
  }, [videoId])

  const checkStatus = useCallback(async () => {
    try {
      const status = await FrameService.getExtractionStatus(videoId)
      setProgress(status)

      if (status.status === 'processing') {
        setIsExtracting(true)
      } else if (status.status === 'completed') {
        setIsExtracting(false)
        fetchFrames()
        if (onCompleted) onCompleted()
      } else if (status.status === 'failed') {
        setIsExtracting(false)
      }
    } catch (err) {
      console.error('Status check error:', err)
    }
  }, [videoId, fetchFrames, onCompleted])

  useEffect(() => {
    checkStatus()
  }, [checkStatus])

  // Polling loop when extraction is processing
  useEffect(() => {
    let intervalId: any
    if (isExtracting) {
      intervalId = setInterval(() => {
        checkStatus()
      }, 1500)
    }
    return () => {
      if (intervalId) clearInterval(intervalId)
    }
  }, [isExtracting, checkStatus])

  const handleStartExtraction = async () => {
    try {
      setIsExtracting(true)
      const res = await FrameService.triggerExtraction(videoId, intervalSeconds)
      setProgress(res)
    } catch (err: any) {
      console.error('Failed to trigger extraction:', err)
      setIsExtracting(false)
    }
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-purple-500/20">
            <Scissors className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">OpenCV Frame Extraction</h3>
            <p className="text-xs text-slate-400">
              Sample video keyframes for downstream AI vector search and object detection
            </p>
          </div>
        </div>

        {/* Configurable Interval Selector */}
        <div className="flex items-center space-x-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
          <Sliders className="w-4 h-4 text-purple-400 ml-2" />
          <span className="text-xs font-semibold text-slate-400">Interval:</span>
          {[0.5, 1.0, 2.0, 5.0].map((sec) => (
            <button
              key={sec}
              type="button"
              onClick={() => setIntervalSeconds(sec)}
              disabled={isExtracting}
              className={`px-2.5 py-1 text-xs font-bold rounded-lg transition ${
                intervalSeconds === sec
                  ? 'bg-purple-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {sec}s
            </button>
          ))}
        </div>
      </div>

      {/* Trigger Button or Active Progress Track */}
      {!isExtracting && (!progress || progress.status === 'pending' || progress.status === 'failed') ? (
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <Sparkles className="w-5 h-5 text-purple-400 shrink-0" />
            <p className="text-xs text-slate-300">
              Extract keyframe images every <strong className="text-purple-300">{intervalSeconds} second(s)</strong> using high-performance OpenCV stream decoder.
            </p>
          </div>

          <button
            onClick={handleStartExtraction}
            className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/25 flex items-center justify-center space-x-2 transition shrink-0"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Extract Keyframes</span>
          </button>
        </div>
      ) : (
        <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {progress?.status === 'completed' ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              ) : progress?.status === 'failed' ? (
                <AlertTriangle className="w-5 h-5 text-red-400" />
              ) : (
                <RefreshCw className="w-5 h-5 text-purple-400 animate-spin" />
              )}
              <div>
                <h4 className="text-sm font-bold text-slate-200">
                  {progress?.status === 'completed'
                    ? `Extraction Complete (${progress.extracted_count} Keyframes)`
                    : progress?.status === 'failed'
                    ? 'Extraction Failed'
                    : 'Extracting OpenCV Keyframes...'}
                </h4>
                <p className="text-xs text-slate-400">
                  Processed {progress?.processed_frames || 0} / {progress?.total_frames || 0} frames (
                  {progress?.progress_percent || 0}%)
                </p>
              </div>
            </div>

            {progress?.retry_count ? progress.retry_count > 0 && (
              <span className="text-[11px] font-semibold text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-md border border-amber-500/20">
                Retry Attempt {progress.retry_count}
              </span>
            ) : null}
          </div>

          {/* Progress bar */}
          <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${
                progress?.status === 'completed'
                  ? 'bg-emerald-500'
                  : progress?.status === 'failed'
                  ? 'bg-red-500'
                  : 'bg-gradient-to-r from-purple-500 via-indigo-500 to-purple-400 animate-pulse'
              }`}
              style={{ width: `${progress?.progress_percent || 0}%` }}
            />
          </div>

          {progress?.error_message && (
            <p className="text-xs text-red-400 font-medium">{progress.error_message}</p>
          )}
        </div>
      )}

      {/* Extracted Keyframe Gallery Grid */}
      {frames.length > 0 && (
        <div className="space-y-4 pt-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-slate-200 font-bold text-sm">
              <ImageIcon className="w-4 h-4 text-indigo-400" />
              <span>Extracted Keyframe Gallery ({frames.length})</span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
            {frames.map((frame) => (
              <div
                key={frame.id}
                onClick={() => setSelectedFrame(frame)}
                className="group relative rounded-xl overflow-hidden bg-slate-950 border border-slate-800 hover:border-purple-500/80 cursor-pointer transition-all hover:scale-[1.03] aspect-video"
              >
                {frame.imageUrl ? (
                  <img
                    src={frame.imageUrl}
                    alt={`Frame ${frame.frameNumber}`}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-slate-600">
                    <ImageIcon className="w-6 h-6" />
                  </div>
                )}

                {/* Badge Overlay */}
                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent p-1.5 flex items-center justify-between text-[10px] text-white">
                  <span className="font-mono bg-black/60 px-1 py-0.2 rounded font-semibold text-purple-300">
                    {formatDuration(frame.timestampSeconds)}
                  </span>
                  <span className="font-mono text-slate-300">#{frame.frameNumber}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Image Modal Lightbox */}
      {selectedFrame && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setSelectedFrame(null)}
        >
          <div
            className="bg-slate-900 border border-slate-800 rounded-2xl p-4 max-w-3xl w-full space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h4 className="text-sm font-bold text-slate-100 flex items-center space-x-2">
                <Clock className="w-4 h-4 text-purple-400" />
                <span>
                  Keyframe at {formatDuration(selectedFrame.timestampSeconds)} (Frame #{selectedFrame.frameNumber})
                </span>
              </h4>
              <button
                onClick={() => setSelectedFrame(null)}
                className="text-xs text-slate-400 hover:text-white px-2 py-1 bg-slate-800 rounded-md"
              >
                Close
              </button>
            </div>

            {selectedFrame.imageUrl && (
              <div className="rounded-xl overflow-hidden bg-black aspect-video">
                <img
                  src={selectedFrame.imageUrl}
                  alt={`Frame ${selectedFrame.frameNumber}`}
                  className="w-full h-full object-contain"
                />
              </div>
            )}

            <div className="grid grid-cols-3 gap-2 text-xs text-slate-300 font-mono bg-slate-950 p-3 rounded-xl">
              <div>Timestamp: {selectedFrame.timestampSeconds}s</div>
              <div>Width: {selectedFrame.width || 'N/A'}px</div>
              <div>Height: {selectedFrame.height || 'N/A'}px</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
