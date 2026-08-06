import React, { useState, useEffect, useCallback } from 'react'
import {
  Scan,
  User,
  Car,
  ShoppingBag,
  Smartphone,
  Laptop,
  Dog,
  Play,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Tag,
  Sliders,
  Sparkles,
} from 'lucide-react'
import { ObjectService } from '@/services/objectService'
import { YOLODetectionProgress, DetectedObject } from '@/types/object_detection'

interface YOLODetectionCardProps {
  videoId: string
  videoTitle: string
}

const CATEGORIES = [
  { id: 'person', label: 'Person', icon: User, color: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/30' },
  { id: 'vehicle', label: 'Vehicle', icon: Car, color: 'text-blue-400 bg-blue-500/10 border-blue-500/30' },
  { id: 'bag', label: 'Bag', icon: ShoppingBag, color: 'text-purple-400 bg-purple-500/10 border-purple-500/30' },
  { id: 'phone', label: 'Phone', icon: Smartphone, color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' },
  { id: 'laptop', label: 'Laptop', icon: Laptop, color: 'text-amber-400 bg-amber-500/10 border-amber-500/30' },
  { id: 'animal', label: 'Animal', icon: Dog, color: 'text-rose-400 bg-rose-500/10 border-rose-500/30' },
]

export const YOLODetectionCard: React.FC<YOLODetectionCardProps> = ({ videoId, videoTitle: _videoTitle }) => {
  const [confidenceThreshold, setConfidenceThreshold] = useState<number>(0.25)
  const [selectedFilterCategory, setSelectedFilterCategory] = useState<string | null>(null)
  const [progress, setProgress] = useState<YOLODetectionProgress | null>(null)
  const [isDetecting, setIsDetecting] = useState<boolean>(false)
  const [detectedObjects, setDetectedObjects] = useState<DetectedObject[]>([])

  const fetchObjects = useCallback(async () => {
    try {
      const data = await ObjectService.getDetectedObjects(
        videoId,
        1,
        60,
        selectedFilterCategory || undefined,
        confidenceThreshold
      )
      setDetectedObjects(data.items || [])
    } catch (err) {
      console.error('Failed to fetch detected objects:', err)
    }
  }, [videoId, selectedFilterCategory, confidenceThreshold])

  const checkStatus = useCallback(async () => {
    try {
      const status = await ObjectService.getDetectionStatus(videoId)
      setProgress(status)

      if (status.status === 'processing') {
        setIsDetecting(true)
      } else if (status.status === 'completed') {
        setIsDetecting(false)
        fetchObjects()
      } else if (status.status === 'failed') {
        setIsDetecting(false)
      }
    } catch (err) {
      console.error('Detection status check error:', err)
    }
  }, [videoId, fetchObjects])

  useEffect(() => {
    checkStatus()
  }, [checkStatus])

  useEffect(() => {
    let intervalId: any
    if (isDetecting) {
      intervalId = setInterval(() => {
        checkStatus()
      }, 1500)
    }
    return () => {
      if (intervalId) clearInterval(intervalId)
    }
  }, [isDetecting, checkStatus])

  const handleStartDetection = async () => {
    try {
      setIsDetecting(true)
      const res = await ObjectService.triggerDetection(videoId, confidenceThreshold)
      setProgress(res)
    } catch (err: any) {
      console.error('Failed to trigger YOLO detection:', err)
      setIsDetecting(false)
    }
  }

  // Count category distribution
  const countsByCategory = CATEGORIES.reduce((acc, cat) => {
    acc[cat.id] = detectedObjects.filter((o) => o.label.toLowerCase() === cat.id).length
    return acc
  }, {} as Record<string, number>)

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20">
            <Scan className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">YOLO Object Detection Pipeline</h3>
            <p className="text-xs text-slate-400">
              Detect Targeted Classes: Person, Vehicle, Bag, Phone, Laptop, Animal
            </p>
          </div>
        </div>

        {/* Confidence Threshold Slider */}
        <div className="flex items-center space-x-3 bg-slate-950 px-3 py-2 rounded-xl border border-slate-800">
          <Sliders className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-semibold text-slate-300">Min Conf:</span>
          <input
            type="range"
            min="0.10"
            max="0.90"
            step="0.05"
            value={confidenceThreshold}
            onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
            disabled={isDetecting}
            className="w-24 accent-emerald-500 cursor-pointer"
          />
          <span className="text-xs font-mono font-bold text-emerald-400 w-8">
            {Math.round(confidenceThreshold * 100)}%
          </span>
        </div>
      </div>

      {/* Target Category Pills */}
      <div className="flex flex-wrap items-center gap-2">
        <button
          onClick={() => setSelectedFilterCategory(null)}
          className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition ${
            selectedFilterCategory === null
              ? 'bg-slate-700 text-white border-slate-600'
              : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
          }`}
        >
          All Classes ({detectedObjects.length})
        </button>

        {CATEGORIES.map((cat) => {
          const Icon = cat.icon
          const count = countsByCategory[cat.id] || 0
          const isSelected = selectedFilterCategory === cat.id
          return (
            <button
              key={cat.id}
              onClick={() => setSelectedFilterCategory(isSelected ? null : cat.id)}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition ${
                isSelected
                  ? 'bg-emerald-600 text-white border-emerald-500 shadow-md'
                  : `${cat.color} hover:brightness-125`
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{cat.label}</span>
              {count > 0 && <span className="ml-1 text-[10px] font-mono opacity-80">({count})</span>}
            </button>
          )
        })}
      </div>

      {/* Trigger Button or Progress Tracker */}
      {!isDetecting && (!progress || progress.status === 'pending' || progress.status === 'failed') ? (
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <Sparkles className="w-5 h-5 text-emerald-400 shrink-0" />
            <p className="text-xs text-slate-300">
              Run YOLO inference on keyframes with <strong className="text-emerald-300">{Math.round(confidenceThreshold * 100)}%</strong> confidence threshold. Stores bounding boxes, labels, and cropped object thumbnails.
            </p>
          </div>

          <button
            onClick={handleStartDetection}
            className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/25 flex items-center justify-center space-x-2 transition shrink-0"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Run YOLO Detection</span>
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
                <RefreshCw className="w-5 h-5 text-emerald-400 animate-spin" />
              )}
              <div>
                <h4 className="text-sm font-bold text-slate-200">
                  {progress?.status === 'completed'
                    ? `YOLO Detection Complete (${progress.detected_objects_count} Objects)`
                    : progress?.status === 'failed'
                    ? 'YOLO Detection Failed'
                    : 'Running YOLO Inference on Keyframes...'}
                </h4>
                <p className="text-xs text-slate-400">
                  Processed {progress?.processed_frames || 0} / {progress?.total_frames || 0} keyframes (
                  {progress?.progress_percent || 0}%)
                </p>
              </div>
            </div>
          </div>

          <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${
                progress?.status === 'completed'
                  ? 'bg-emerald-500'
                  : progress?.status === 'failed'
                  ? 'bg-red-500'
                  : 'bg-gradient-to-r from-emerald-500 via-teal-500 to-indigo-400 animate-pulse'
              }`}
              style={{ width: `${progress?.progress_percent || 0}%` }}
            />
          </div>

          {progress?.error_message && (
            <p className="text-xs text-red-400 font-medium">{progress.error_message}</p>
          )}
        </div>
      )}

      {/* Detected Objects Grid */}
      {detectedObjects.length > 0 && (
        <div className="space-y-4 pt-2">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
              <Tag className="w-4 h-4 text-emerald-400" />
              <span>Detected Objects Payload ({detectedObjects.length})</span>
            </h4>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {detectedObjects.map((obj) => (
              <div
                key={obj.id}
                className="bg-slate-950 border border-slate-800 rounded-xl p-3 space-y-2 hover:border-emerald-500/50 transition group"
              >
                {/* Object Thumbnail or Bounding Box Preview */}
                <div className="aspect-square bg-slate-900 rounded-lg overflow-hidden flex items-center justify-center relative">
                  {obj.cropUrl ? (
                    <img src={obj.cropUrl} alt={obj.label} className="w-full h-full object-cover" />
                  ) : (
                    <div className="flex flex-col items-center justify-center text-slate-600">
                      <Scan className="w-6 h-6" />
                      <span className="text-[10px] font-mono mt-1">
                        [{obj.boundingBox.xmin.toFixed(2)}, {obj.boundingBox.ymin.toFixed(2)}]
                      </span>
                    </div>
                  )}
                  <span className="absolute top-1 right-1 bg-black/70 backdrop-blur-md px-1.5 py-0.5 rounded text-[10px] font-mono font-bold text-emerald-400 border border-emerald-500/30">
                    {Math.round(obj.confidence * 100)}%
                  </span>
                </div>

                {/* Class Label and Frame Info */}
                <div className="space-y-0.5">
                  <span className="text-xs font-bold text-slate-200 capitalize truncate block">
                    {obj.label}
                  </span>
                  <p className="text-[10px] text-slate-400 font-mono">
                    Frame #{obj.frameNumber || 'N/A'} ({obj.timestampSeconds ? `${obj.timestampSeconds}s` : 'N/A'})
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
