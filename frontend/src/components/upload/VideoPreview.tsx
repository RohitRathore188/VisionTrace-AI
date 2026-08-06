import React, { useRef, useState } from 'react'
import { Play, Pause, Volume2, VolumeX, Maximize2, Clock, Monitor, HardDrive, RefreshCw } from 'lucide-react'
import { VideoMetadata } from '@/types/video'
import { formatBytes, formatDuration } from '@/lib/videoValidation'

interface VideoPreviewProps {
  src: string
  file: File
  metadata?: VideoMetadata | null
  onReset: () => void
  disabled?: boolean
}

export const VideoPreview: React.FC<VideoPreviewProps> = ({
  src,
  file,
  metadata,
  onReset,
  disabled = false,
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)

  const togglePlay = () => {
    if (!videoRef.current) return
    if (isPlaying) {
      videoRef.current.pause()
      setIsPlaying(false)
    } else {
      videoRef.current.play()
      setIsPlaying(true)
    }
  }

  const toggleMute = () => {
    if (!videoRef.current) return
    videoRef.current.muted = !isMuted
    setIsMuted(!isMuted)
  }

  const handleFullscreen = () => {
    if (videoRef.current) {
      if (videoRef.current.requestFullscreen) {
        videoRef.current.requestFullscreen()
      }
    }
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 overflow-hidden space-y-4">
      {/* Video Player Container */}
      <div className="relative rounded-xl overflow-hidden bg-black aspect-video group">
        <video
          ref={videoRef}
          src={src}
          className="w-full h-full object-contain"
          onEnded={() => setIsPlaying(false)}
        />

        {/* Video Overlay Controls */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-between p-4">
          <div className="flex justify-between items-center">
            <span className="text-xs font-semibold text-white/90 bg-black/50 backdrop-blur-md px-2.5 py-1 rounded-md border border-white/10 truncate max-w-[200px]">
              {file.name}
            </span>
            {!disabled && (
              <button
                type="button"
                onClick={onReset}
                className="flex items-center space-x-1 text-xs font-medium text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-700 backdrop-blur-md px-2.5 py-1 rounded-md border border-slate-700 transition"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Change Video</span>
              </button>
            )}
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                type="button"
                onClick={togglePlay}
                className="w-9 h-9 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center transition shadow-md"
              >
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
              </button>
              <button
                type="button"
                onClick={toggleMute}
                className="p-2 text-slate-300 hover:text-white bg-black/40 hover:bg-black/60 rounded-lg transition"
              >
                {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              </button>
            </div>
            <button
              type="button"
              onClick={handleFullscreen}
              className="p-2 text-slate-300 hover:text-white bg-black/40 hover:bg-black/60 rounded-lg transition"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Metadata Badges Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-2.5 flex items-center space-x-2.5">
          <Clock className="w-4 h-4 text-indigo-400 shrink-0" />
          <div className="min-w-0">
            <p className="text-[10px] uppercase font-semibold text-slate-400">Duration</p>
            <p className="text-xs font-bold text-slate-200 truncate">
              {formatDuration(metadata?.durationSeconds)}
            </p>
          </div>
        </div>

        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-2.5 flex items-center space-x-2.5">
          <Monitor className="w-4 h-4 text-purple-400 shrink-0" />
          <div className="min-w-0">
            <p className="text-[10px] uppercase font-semibold text-slate-400">Resolution</p>
            <p className="text-xs font-bold text-slate-200 truncate">
              {metadata?.width && metadata?.height ? `${metadata.width}x${metadata.height}` : 'N/A'}
            </p>
          </div>
        </div>

        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-2.5 flex items-center space-x-2.5">
          <HardDrive className="w-4 h-4 text-emerald-400 shrink-0" />
          <div className="min-w-0">
            <p className="text-[10px] uppercase font-semibold text-slate-400">File Size</p>
            <p className="text-xs font-bold text-slate-200 truncate">{formatBytes(file.size)}</p>
          </div>
        </div>

        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-2.5 flex items-center space-x-2.5">
          <div className="w-4 h-4 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-[10px] font-bold">
            F
          </div>
          <div className="min-w-0">
            <p className="text-[10px] uppercase font-semibold text-slate-400">Format</p>
            <p className="text-xs font-bold text-slate-200 truncate uppercase">
              {file.name.split('.').pop() || 'MP4'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
